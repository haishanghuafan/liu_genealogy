"""
Tenant management CLI commands
"""
import asyncio
import uuid
from datetime import datetime, timezone
from typing import Optional

import asyncpg
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import db_manager
from app.models.system import Tenant


async def create_tenant_schema(tenant: Tenant) -> None:
    """Create PostgreSQL schema and Neo4j database for a tenant"""
    
    # Create PostgreSQL schema
    schema_name = tenant.schema_name
    
    # Get connection to default database
    conn = await asyncpg.connect(
        host="localhost",
        port=5432,
        user="postgres",
        password="postgres",
        database="genealogy"
    )
    
    try:
        # Create schema
        await conn.execute(f'CREATE SCHEMA IF NOT EXISTS "{schema_name}"')
        print(f"✓ Created PostgreSQL schema: {schema_name}")
        
        # Grant permissions (optional, for now full access)
        # await conn.execute(f'GRANT ALL ON SCHEMA {schema_name} TO postgres')
        
    finally:
        await conn.close()
    
    print(f"✓ Tenant database setup complete: {schema_name}")


async def create_tenant_schema_psycopg() -> None:
    """Alternative using psycopg3 sync"""
    import psycopg
    
    conn = psycopg.connect(
        host="localhost",
        port=5432,
        user="postgres",
        password="postgres",
        dbname="genealogy"
    )
    
    try:
        # Create schema
        with conn.cursor() as cur:
            cur.execute('CREATE SCHEMA IF NOT EXISTS tenant_liu_qianzheng')
            print("✓ Created schema")
            conn.commit()
    finally:
        conn.close()


async def init_tenant_tables(schema_name: str) -> None:
    """Initialize tables in tenant schema"""
    
    # This would be done via Alembic with tenant-specific configuration
    # For now, we'll create tables directly
    
    conn = await asyncpg.connect(
        host="localhost",
        port=5432,
        user="postgres",
        password="postgres",
        database="genealogy"
    )
    
    try:
        # Set search path
        await conn.execute(f'SET search_path TO {schema_name}')
        
        # Create tables...
        # generations
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS generations (
                id SERIAL PRIMARY KEY,
                number INTEGER NOT NULL,
                is_spouse BOOLEAN DEFAULT FALSE,
                name VARCHAR(50),
                description TEXT,
                UNIQUE(number, is_spouse)
            )
        ''')
        
        # branches
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS branches (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                name VARCHAR(100) NOT NULL,
                founder_id UUID,
                description TEXT,
                location VARCHAR(200)
            )
        ''')
        
        # persons
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS persons (
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
        
        # spouse_relations
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS spouse_relations (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                husband_id UUID NOT NULL,
                wife_id UUID NOT NULL,
                relation_type VARCHAR(20) DEFAULT 'marriage',
                source_info VARCHAR(200),
                sort_order INTEGER DEFAULT 1,
                UNIQUE(husband_id, wife_id)
            )
        ''')
        
        # person_images
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS person_images (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                person_id UUID NOT NULL,
                url VARCHAR(500) NOT NULL,
                title VARCHAR(100),
                description TEXT,
                sort_order INTEGER DEFAULT 0,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            )
        ''')
        
        # person_videos
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS person_videos (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                person_id UUID NOT NULL,
                url VARCHAR(500) NOT NULL,
                title VARCHAR(100),
                description TEXT,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            )
        ''')
        
        # change_logs
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS change_logs (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                table_name VARCHAR(50) NOT NULL,
                record_id UUID NOT NULL,
                action VARCHAR(20) NOT NULL,
                old_values JSONB,
                new_values JSONB,
                changed_by UUID,
                changed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                review_status VARCHAR(20) DEFAULT 'pending',
                reviewed_by UUID,
                reviewed_at TIMESTAMP WITH TIME ZONE,
                review_notes TEXT
            )
        ''')
        
        print(f"✓ Created tables in schema: {schema_name}")
        
    finally:
        await conn.close()


async def create_neo4j_database(db_name: str) -> None:
    """Create Neo4j database for tenant"""
    from neo4j import GraphDatabase
    
    driver = GraphDatabase.driver(
        "bolt://localhost:7687",
        auth=("neo4j", "password123")
    )
    
    try:
        with driver.session() as session:
            # Create database if not exists (Neo4j 5+)
            # Note: Requires Neo4j Enterprise for multiple databases
            # For community edition, we'll use a different approach
            # by adding tenant prefix to all nodes
            
            # For now, just verify connection
            result = session.run("RETURN 1 as test")
            print(f"✓ Neo4j connection OK for: {db_name}")
    finally:
        driver.close()


async def create_tenant(
    name: str,
    slug: str,
    surname: str,
    is_public: bool = True,
) -> Tenant:
    """Create a new tenant with all required setup"""
    
    # Generate schema name from slug
    schema_name = f"tenant_{slug.replace('-', '_')}"
    neo4j_db = f"tenant_{slug}"
    
    # Create tenant in memory
    tenant = Tenant(
        id=uuid.uuid4(),
        name=name,
        slug=slug,
        surname=surname,
        schema_name=schema_name,
        neo4j_database=neo4j_db,
        plan="free",
        max_members=100,
        max_persons=500,
        max_storage_mb=500,
        is_active=True,
        is_public=is_public,
        created_at=datetime.now(timezone.utc),
    )
    
    # Save to database
    session_maker = db_manager.get_session_maker("public")
    async with session_maker() as session:
        session.add(tenant)
        await session.commit()
        await session.refresh(tenant)
    
    # Create PostgreSQL schema
    await create_tenant_schema(tenant)
    
    # Initialize tables in tenant schema
    await init_tenant_tables(schema_name)
    
    # Setup Neo4j
    await create_neo4j_database(neo4j_db)
    
    print(f"\n✓ Tenant created successfully!")
    print(f"  Name: {tenant.name}")
    print(f"  Slug: {tenant.slug}")
    print(f"  Schema: {tenant.schema_name}")
    print(f"  Neo4j DB: {tenant.neo4j_database}")
    
    return tenant


async def main():
    """CLI entry point"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python -m scripts.create_tenant <slug>")
        print("Example: python -m scripts.create_tenant liu-qianzheng")
        sys.exit(1)
    
    slug = sys.argv[1]
    
    # For demo, use hardcoded values
    tenant = await create_tenant(
        name="刘氏乾正公族谱",
        slug=slug,
        surname="刘",
        is_public=True,
    )


if __name__ == "__main__":
    asyncio.run(main())