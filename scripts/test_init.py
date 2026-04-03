#!/usr/bin/env python3
"""
Test initialization with SQLite (no external dependencies)
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))


async def test_init():
    """Test system initialization with SQLite"""
    
    print("🧪 Testing System Initialization (SQLite)")
    print("=" * 50)
    
    try:
        import aiosqlite
        
        # Create test database
        db_path = Path(__file__).parent / "test.db"
        if db_path.exists():
            db_path.unlink()
        
        print(f"\n📦 Creating SQLite database: {db_path}")
        
        conn = await aiosqlite.connect(str(db_path))
        
        # Enable foreign keys
        await conn.execute("PRAGMA foreign_keys = ON")
        
        print("\n1️⃣ Creating system tables...")
        
        # Users table
        await conn.execute('''
            CREATE TABLE users (
                id TEXT PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                nickname TEXT,
                system_role TEXT NOT NULL DEFAULT 'user',
                is_active INTEGER NOT NULL DEFAULT 1
            )
        ''')
        
        # Tenants table
        await conn.execute('''
            CREATE TABLE tenants (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                slug TEXT UNIQUE NOT NULL,
                surname TEXT NOT NULL,
                schema_name TEXT UNIQUE NOT NULL,
                is_active INTEGER NOT NULL DEFAULT 1
            )
        ''')
        
        # Tenant users table
        await conn.execute('''
            CREATE TABLE tenant_users (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                tenant_id TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'member',
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (tenant_id) REFERENCES tenants(id)
            )
        ''')
        
        print("   ✓ System tables created")
        
        print("\n2️⃣ Creating superuser...")
        import uuid
        from passlib.context import CryptContext
        
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        
        admin_id = str(uuid.uuid4())
        admin_email = "admin@test.com"
        admin_password = "admin123"
        
        await conn.execute(
            'INSERT INTO users (id, email, password_hash, system_role, is_active) VALUES (?, ?, ?, ?, 1)',
            (admin_id, admin_email, pwd_context.hash(admin_password), 'super_admin')
        )
        print(f"   ✓ Admin: {admin_email}")
        
        print("\n3️⃣ Creating tenant...")
        tenant_id = str(uuid.uuid4())
        tenant_name = "刘氏测试族谱"
        tenant_slug = "liu-test"
        
        await conn.execute(
            'INSERT INTO tenants (id, name, slug, surname, schema_name, is_active) VALUES (?, ?, ?, ?, ?, 1)',
            (tenant_id, tenant_name, tenant_slug, "刘", f"tenant_{tenant_slug}")
        )
        print(f"   ✓ Tenant: {tenant_name}")
        
        print("\n4️⃣ Creating tenant schema (persons table)...")
        
        await conn.execute('''
            CREATE TABLE persons (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                gender TEXT DEFAULT 'M',
                generation_id INTEGER,
                father_id TEXT,
                mother_id TEXT,
                birth_year INTEGER,
                death_year INTEGER,
                visibility TEXT DEFAULT 'public'
            )
        ''')
        print("   ✓ Persons table created")
        
        print("\n5️⃣ Adding test persons...")
        
        persons = [
            (str(uuid.uuid4()), "刘一世", "M", 1, None, None, 1800, 1870, "public"),
            (str(uuid.uuid4()), "刘二世", "M", 2, None, None, 1830, 1900, "public"),
            (str(uuid.uuid4()), "刘三世", "M", 3, None, None, 1860, 1930, "public"),
        ]
        
        # Set father relationships
        persons[1] = (persons[1][0], persons[1][1], persons[1][2], persons[1][3], persons[0][0], None, persons[1][6], persons[1][7], persons[1][8])
        persons[2] = (persons[2][0], persons[2][1], persons[2][2], persons[2][3], persons[1][0], None, persons[2][6], persons[2][7], persons[2][8])
        
        for p in persons:
            await conn.execute(
                'INSERT INTO persons (id, name, gender, generation_id, father_id, mother_id, birth_year, death_year, visibility) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                p
            )
        print(f"   ✓ Added {len(persons)} test persons")
        
        print("\n6️⃣ Linking admin to tenant...")
        await conn.execute(
            'INSERT INTO tenant_users (id, user_id, tenant_id, role) VALUES (?, ?, ?, ?)',
            (str(uuid.uuid4()), admin_id, tenant_id, 'tenant_admin')
        )
        print("   ✓ Admin linked")
        
        # Verify data
        print("\n7️⃣ Verifying data...")
        
        user_count = await (await conn.execute('SELECT COUNT(*) FROM users')).fetchone()
        tenant_count = await (await conn.execute('SELECT COUNT(*) FROM tenants')).fetchone()
        person_count = await (await conn.execute('SELECT COUNT(*) FROM persons')).fetchone()
        
        print(f"   Users: {user_count[0]}")
        print(f"   Tenants: {tenant_count[0]}")
        print(f"   Persons: {person_count[0]}")
        
        await conn.close()
        
        print("\n" + "=" * 50)
        print("✅ Test initialization complete!")
        print(f"\n   Database: {db_path}")
        print(f"   Login: {admin_email}")
        print(f"   Password: {admin_password}")
        
        return True
        
    except ImportError as e:
        print(f"\n❌ Missing dependency: {e}")
        print("   Run: pip install aiosqlite passlib")
        return False
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_init())
    sys.exit(0 if success else 1)