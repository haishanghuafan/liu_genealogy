#!/usr/bin/env python3
"""
System Initialization Script
- Creates database schemas
- Initializes system tables
- Creates first superuser
- Creates first tenant
"""
import asyncio
import os
import sys
from pathlib import Path
from uuid import uuid4

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

import asyncpg
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def init_system():
    """Initialize the entire system"""
    
    print("🚀 Genealogy SaaS System Initialization")
    print("=" * 50)
    
    # Database connection info
    db_host = os.getenv("POSTGRES_HOST", "localhost")
    db_port = int(os.getenv("POSTGRES_PORT", "5432"))
    db_user = os.getenv("POSTGRES_USER", "postgres")
    db_password = os.getenv("POSTGRES_PASSWORD", "postgres")
    db_name = os.getenv("POSTGRES_DB", "genealogy")
    
    print(f"\n📦 Connecting to PostgreSQL: {db_host}:{db_port}/{db_name}")
    
    # Connect to PostgreSQL
    conn = await asyncpg.connect(
        host=db_host,
        port=db_port,
        user=db_user,
        password=db_password,
        database=db_name
    )
    
    try:
        # Step 1: Create extensions
        print("\n1️⃣ Creating database extensions...")
        await conn.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
        await conn.execute('CREATE EXTENSION IF NOT EXISTS "pg_trgm"')
        print("   ✓ Extensions created")
        
        # Step 2: Create system tables
        print("\n2️⃣ Creating system tables...")
        await create_system_tables(conn)
        print("   ✓ System tables created")
        
        # Step 3: Create superuser
        print("\n3️⃣ Creating superuser...")
        admin_email = os.getenv("ADMIN_EMAIL", "admin@example.com")
        admin_password = os.getenv("ADMIN_PASSWORD", "admin123")
        admin_id = await create_superuser(conn, admin_email, admin_password)
        print(f"   ✓ Superuser created: {admin_email}")
        
        # Step 4: Create first tenant
        print("\n4️⃣ Creating first tenant...")
        tenant_name = os.getenv("TENANT_NAME", "刘氏乾正公族谱")
        tenant_slug = os.getenv("TENANT_SLUG", "liu-qianzheng")
        tenant_surname = os.getenv("TENANT_SURNAME", "刘")
        tenant_id = await create_tenant(conn, tenant_name, tenant_slug, tenant_surname, admin_id)
        print(f"   ✓ Tenant created: {tenant_name} ({tenant_slug})")
        
        # Step 5: Create tenant schema and tables
        print("\n5️⃣ Creating tenant schema...")
        schema_name = f"tenant_{tenant_slug.replace('-', '_')}"
        await create_tenant_schema(conn, schema_name)
        print(f"   ✓ Schema created: {schema_name}")
        
        # Step 6: Link user to tenant
        print("\n6️⃣ Linking admin to tenant...")
        await link_user_to_tenant(conn, admin_id, tenant_id)
        print("   ✓ Admin linked as tenant administrator")
        
        print("\n" + "=" * 50)
        print("✅ System initialization complete!")
        print("\n📋 Summary:")
        print(f"   Superuser: {admin_email}")
        print(f"   Password:  {admin_password}")
        print(f"   Tenant:    {tenant_name}")
        print(f"   Slug:      {tenant_slug}")
        print(f"   Schema:    {schema_name}")
        print("\n🌐 Next steps:")
        print("   1. Start the API server: uvicorn app.main:app --reload")
        print("   2. Start the frontend: cd frontend && npm run dev")
        print(f"   3. Visit: http://localhost:3010/t/{tenant_slug}/family-tree")
        
    finally:
        await conn.close()


async def create_system_tables(conn: asyncpg.Connection):
    """Create system tables"""
    
    # Tenants table
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
    
    # Create index
    await conn.execute('CREATE INDEX IF NOT EXISTS ix_tenants_slug ON tenants(slug)')
    
    # Users table
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
    
    # Create index
    await conn.execute('CREATE INDEX IF NOT EXISTS ix_users_email ON users(email)')
    
    # Tenant-Users table
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
    
    # Create indexes
    await conn.execute('CREATE INDEX IF NOT EXISTS ix_tenant_users_user_id ON tenant_users(user_id)')
    await conn.execute('CREATE INDEX IF NOT EXISTS ix_tenant_users_tenant_id ON tenant_users(tenant_id)')
    
    # Subscriptions table
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS subscriptions (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
            plan VARCHAR(20) NOT NULL,
            amount FLOAT,
            currency VARCHAR(10) NOT NULL DEFAULT 'CNY',
            started_at TIMESTAMP WITH TIME ZONE NOT NULL,
            expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
            status VARCHAR(20) NOT NULL DEFAULT 'active',
            payment_id VARCHAR(100),
            created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
        )
    ''')
    
    await conn.execute('CREATE INDEX IF NOT EXISTS ix_subscriptions_tenant_id ON subscriptions(tenant_id)')


async def create_superuser(conn: asyncpg.Connection, email: str, password: str) -> str:
    """Create superuser"""
    
    # Check if already exists
    existing = await conn.fetchval(
        'SELECT id FROM users WHERE email = $1',
        email
    )
    
    if existing:
        print(f"   ! User {email} already exists, skipping")
        return str(existing)
    
    # Create user
    password_hash = pwd_context.hash(password)
    
    user_id = await conn.fetchval('''
        INSERT INTO users (email, password_hash, system_role, is_active, email_verified)
        VALUES ($1, $2, 'super_admin', TRUE, TRUE)
        RETURNING id
    ''', email, password_hash)
    
    return str(user_id)


async def create_tenant(
    conn: asyncpg.Connection,
    name: str,
    slug: str,
    surname: str,
    admin_id: str
) -> str:
    """Create tenant"""
    
    # Check if already exists
    existing = await conn.fetchval(
        'SELECT id FROM tenants WHERE slug = $1',
        slug
    )
    
    if existing:
        print(f"   ! Tenant {slug} already exists, skipping")
        return str(existing)
    
    schema_name = f"tenant_{slug.replace('-', '_')}"
    neo4j_db = f"tenant_{slug}"
    
    tenant_id = await conn.fetchval('''
        INSERT INTO tenants (name, slug, surname, schema_name, neo4j_database, plan, is_active, is_public)
        VALUES ($1, $2, $3, $4, $5, 'pro', TRUE, TRUE)
        RETURNING id
    ''', name, slug, surname, schema_name, neo4j_db)
    
    return str(tenant_id)


async def create_tenant_schema(conn: asyncpg.Connection, schema_name: str):
    """Create tenant schema and tables"""
    
    # Create schema
    await conn.execute(f'CREATE SCHEMA IF NOT EXISTS "{schema_name}"')
    
    # Generations table
    await conn.execute(f'''
        CREATE TABLE IF NOT EXISTS "{schema_name}".generations (
            id SERIAL PRIMARY KEY,
            number INTEGER NOT NULL,
            is_spouse BOOLEAN DEFAULT FALSE,
            name VARCHAR(50),
            description TEXT,
            UNIQUE(number, is_spouse)
        )
    ''')
    
    # Branches table
    await conn.execute(f'''
        CREATE TABLE IF NOT EXISTS "{schema_name}".branches (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            name VARCHAR(100) NOT NULL,
            founder_id UUID,
            description TEXT,
            location VARCHAR(200)
        )
    ''')
    
    # Persons table
    await conn.execute(f'''
        CREATE TABLE IF NOT EXISTS "{schema_name}".persons (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            name VARCHAR(100) NOT NULL,
            courtesy_name VARCHAR(100),
            art_name VARCHAR(100),
            alias VARCHAR(100),
            generation_char VARCHAR(10),
            gender VARCHAR(1) DEFAULT 'M',
            is_outsider BOOLEAN DEFAULT FALSE,
            generation_id INTEGER,
            father_id UUID,
            mother_id UUID,
            branch_id UUID,
            birth_year INTEGER,
            death_year INTEGER,
            birth_place VARCHAR(200),
            lunar_birthday VARCHAR(50),
            burial_place VARCHAR(300),
            burial_fengshui VARCHAR(200),
            burial_direction VARCHAR(100),
            biography TEXT,
            achievements TEXT,
            descendants_location TEXT,
            notes TEXT,
            visibility VARCHAR(20) DEFAULT 'public',
            sort_order INTEGER DEFAULT 0,
            avatar VARCHAR(500),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            created_by UUID
        )
    ''')
    
    # Spouse relations table
    await conn.execute(f'''
        CREATE TABLE IF NOT EXISTS "{schema_name}".spouse_relations (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            husband_id UUID NOT NULL,
            wife_id UUID NOT NULL,
            relation_type VARCHAR(20) DEFAULT 'marriage',
            source_info VARCHAR(200),
            sort_order INTEGER DEFAULT 1,
            UNIQUE(husband_id, wife_id)
        )
    ''')
    
    # Person images table
    await conn.execute(f'''
        CREATE TABLE IF NOT EXISTS "{schema_name}".person_images (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            person_id UUID NOT NULL,
            url VARCHAR(500) NOT NULL,
            title VARCHAR(100),
            description TEXT,
            sort_order INTEGER DEFAULT 0,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        )
    ''')
    
    # Person videos table
    await conn.execute(f'''
        CREATE TABLE IF NOT EXISTS "{schema_name}".person_videos (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            person_id UUID NOT NULL,
            url VARCHAR(500) NOT NULL,
            title VARCHAR(100),
            description TEXT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        )
    ''')
    
    # Change logs table
) -> None:
    await conn.execute(f'''
        CREATE TABLE IF NOT EXISTS "{schema_name}".change_logs (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            table_name VARCHAR(50) NOT NULL,
            record_id UUID NOT NULL,
            action VARCHAR(20) NOT NULL,
            old_values JSON&,
            new_values JSONB,
            changed_by UUID,
            changed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            review_status VARCHAR(20) DEFAULT 'pending',
            reviewed_by UUID,
            reviewed_at TIMESTAMP WITH TIME ZONE,
            review_notes TEXT
        )
    ''')


async def link_user_to_tenant(conn: asyncpg.Connection, user_id: str, tenant_id: str):
    """Link user to tenant as administrator"""
    
    # Check if already linked
    existing = await conn.fetchval('''
        SELECT id FROM tenant_users
        WHERE user_id = $1 AND tenant_id = $2
    ''', user_id, tenant_id)
    
    if existing:
        return
    
    await conn.execute('''
        INSERT INTO tenant_users (user_id, tenant_id, role)
        VALUES ($1, $2, 'tenant_admin')
    ''', user_id, tenant_id)


if __name__ == "__main__":
    asyncio.run(init_system())
