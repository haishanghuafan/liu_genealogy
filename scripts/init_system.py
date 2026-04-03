#!/usr/bin/env python3
"""
System Initialization Script
"""
import asyncio
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

import asyncpg
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def init_system():
    """Initialize the entire system"""
    
    print("🚀 Genealogy SaaS System Initialization")
    print("=" * 50)
    
    db_host = os.getenv("POSTGRES_HOST", "localhost")
    db_port = int(os.getenv("POSTGRES_PORT", "5432"))
    db_user = os.getenv("POSTGRES_USER", "postgres")
    db_password = os.getenv("POSTGRES_PASSWORD", "postgres")
    db_name = os.getenv("POSTGRES_DB", "genealogy")
    
    print(f"\n📦 Connecting to PostgreSQL: {db_host}:{db_port}/{db_name}")
    
    conn = await asyncpg.connect(
        host=db_host, port=db_port, user=db_user,
        password=db_password, database=db_name
    )
    
    try:
        print("\n1️⃣ Creating database extensions...")
        await conn.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
        await conn.execute('CREATE EXTENSION IF NOT EXISTS "pg_trgm"')
        print("   ✓ Extensions created")
        
        print("\n2️⃣ Creating system tables...")
        await create_system_tables(conn)
        print("   ✓ System tables created")
        
        print("\n3️⃣ Creating superuser...")
        admin_email = os.getenv("ADMIN_EMAIL", "admin@example.com")
        admin_password = os.getenv("ADMIN_PASSWORD", "admin123")
        admin_id = await create_superuser(conn, admin_email, admin_password)
        print(f"   ✓ Superuser: {admin_email}")
        
        print("\n4️⃣ Creating first tenant...")
        tenant_name = os.getenv("TENANT_NAME", "刘氏乾正公族谱")
        tenant_slug = os.getenv("TENANT_SLUG", "liu-qianzheng")
        tenant_surname = os.getenv("TENANT_SURNAME", "刘")
        tenant_id = await create_tenant(conn, tenant_name, tenant_slug, tenant_surname)
        print(f"   ✓ Tenant: {tenant_name}")
        
        print("\n5️⃣ Creating tenant schema...")
        schema_name = f"tenant_{tenant_slug.replace('-', '_')}"
        await create_tenant_schema(conn, schema_name)
        print(f"   ✓ Schema: {schema_name}")
        
        print("\n6️⃣ Linking admin to tenant...")
        await link_user_to_tenant(conn, admin_id, tenant_id)
        print("   ✓ Admin linked")
        
        print("\n" + "=" * 50)
        print("✅ System initialization complete!")
        print(f"\n   Login: {admin_email}")
        print(f"   Password: {admin_password}")
        print(f"   Tenant: {tenant_slug}")
        
    finally:
        await conn.close()


async def create_system_tables(conn):
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS tenants (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            name VARCHAR(100) NOT NULL,
            slug VARCHAR(50) UNIQUE NOT NULL,
            surname VARCHAR(50) NOT NULL,
            schema_name VARCHAR(50) UNIQUE NOT NULL,
            neo4j_database VARCHAR(50) NOT NULL,
            plan VARCHAR(20) NOT NULL DEFAULT 'free',
            max_members INTEGER NOT NULL DEFAULT 100,
            max_persons INTEGER NOT NULL DEFAULT 500,
            max_storage_mb INTEGER NOT NULL DEFAULT 500,
            is_active BOOLEAN NOT NULL DEFAULT TRUE,
            is_public BOOLEAN NOT NULL DEFAULT TRUE,
            created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
            expires_at TIMESTAMP WITH TIME ZONE,
            settings JSONB DEFAULT '{}'
        )
    ''')
    await conn.execute('CREATE INDEX IF NOT EXISTS ix_tenants_slug ON tenants(slug)')
    
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            email VARCHAR(255) UNIQUE NOT NULL,
            phone VARCHAR(20) UNIQUE,
            password_hash VARCHAR(255) NOT NULL,
            nickname VARCHAR(50),
            avatar VARCHAR(500),
            system_role VARCHAR(20) NOT NULL DEFAULT 'user',
            is_active BOOLEAN NOT NULL DEFAULT TRUE,
            email_verified BOOLEAN NOT NULL DEFAULT FALSE,
            created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
            last_login_at TIMESTAMP WITH TIME ZONE
        )
    ''')
    await conn.execute('CREATE INDEX IF NOT EXISTS ix_users_email ON users(email)')
    
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS tenant_users (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
            role VARCHAR(20) NOT NULL DEFAULT 'member',
            person_id UUID,
            joined_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
            invited_by UUID
        )
    ''')
    await conn.execute('CREATE INDEX IF NOT EXISTS ix_tenant_users_user_id ON tenant_users(user_id)')
    await conn.execute('CREATE INDEX IF NOT EXISTS ix_tenant_users_tenant_id ON tenant_users(tenant_id)')


async def create_superuser(conn, email, password):
    existing = await conn.fetchval('SELECT id FROM users WHERE email = $1', email)
    if existing:
        return existing
    password_hash = pwd_context.hash(password)
    return await conn.fetchval(
        'INSERT INTO users (email, password_hash, system_role, is_active) VALUES ($1, $2, $3, TRUE) RETURNING id',
        email, password_hash, 'super_admin'
    )


async def create_tenant(conn, name, slug, surname):
    existing = await conn.fetchval('SELECT id FROM tenants WHERE slug = $1', slug)
    if existing:
        return existing
    schema_name = f"tenant_{slug.replace('-', '_')}"
    return await conn.fetchval(
        'INSERT INTO tenants (name, slug, surname, schema_name, neo4j_database, is_active) VALUES ($1, $2, $3, $4, $5, TRUE) RETURNING id',
        name, slug, surname, schema_name, f"tenant_{slug}"
    )


async def create_tenant_schema(conn, schema_name):
    await conn.execute(f'CREATE SCHEMA IF NOT EXISTS "{schema_name}"')
    
    await conn.execute(f'''
        CREATE TABLE IF NOT EXISTS "{schema_name}".generations (
            id SERIAL PRIMARY KEY, number INTEGER NOT NULL,
            is_spouse BOOLEAN DEFAULT FALSE, name VARCHAR(50), description TEXT,
            UNIQUE(number, is_spouse)
        )
    ''')
    
    await conn.execute(f'''
        CREATE TABLE IF NOT EXISTS "{schema_name}".branches (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            name VARCHAR(100) NOT NULL, founder_id UUID,
            description TEXT, location VARCHAR(200)
        )
    ''')
    
    await conn.execute(f'''
        CREATE TABLE IF NOT EXISTS "{schema_name}".persons (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            name VARCHAR(100) NOT NULL, courtesy_name VARCHAR(100),
            art_name VARCHAR(100), alias VARCHAR(100),
            generation_char VARCHAR(10), gender VARCHAR(1) DEFAULT 'M',
            is_outsider BOOLEAN DEFAULT FALSE, generation_id INTEGER,
            father_id UUID, mother_id UUID, branch_id UUID,
            birth_year INTEGER, death_year INTEGER, birth_place VARCHAR(200),
            lunar_birthday VARCHAR(50), burial_place VARCHAR(300),
            burial_fengshui VARCHAR(200), burial_direction VARCHAR(100),
            biography TEXT, achievements TEXT, descendants_location TEXT,
            notes TEXT, visibility VARCHAR(20) DEFAULT 'public',
            sort_order INTEGER DEFAULT 0, avatar VARCHAR(500),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(), created_by UUID
        )
    ''')
    
    await conn.execute(f'''
        CREATE TABLE IF NOT EXISTS "{schema_name}".spouse_relations (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            husband_id UUID NOT NULL, wife_id UUID NOT NULL,
            relation_type VARCHAR(20) DEFAULT 'marriage',
            source_info VARCHAR(200), sort_order INTEGER DEFAULT 1,
            UNIQUE(husband_id, wife_id)
        )
    ''')


async def link_user_to_tenant(conn, user_id, tenant_id):
    existing = await conn.fetchval(
        'SELECT id FROM tenant_users WHERE user_id = $1 AND tenant_id = $2',
        user_id, tenant_id
    )
    if not existing:
        await conn.execute(
            'INSERT INTO tenant_users (user_id, tenant_id, role) VALUES ($1, $2, $3)',
            user_id, tenant_id, 'tenant_admin'
        )


if __name__ == "__main__":
    asyncio.run(init_system())
