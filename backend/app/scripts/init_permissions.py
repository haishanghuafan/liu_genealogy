"""
Initialize permissions and roles

Usage:
    cd backend
    .\venv\Scripts\python.exe -m app.scripts.init_permissions
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.core.config import settings
from app.core.permissions import SYSTEM_PERMISSIONS, BUILTIN_ROLES, BUILTIN_TENANT_ROLES
from app.models.system import Permission, Role, RolePermission


async def init_permissions():
    """Initialize permissions and built-in roles"""
    engine = create_async_engine(settings.database_url)
    async with async_sessionmaker(engine)() as session:
        # Seed permissions
        existing_codes = set()
        stmt = select(Permission.code)
        result = await session.execute(stmt)
        existing_codes = set(result.scalars().all())
        
        new_perms = 0
        for perm_data in SYSTEM_PERMISSIONS:
            if perm_data["code"] not in existing_codes:
                perm = Permission(
                    code=perm_data["code"],
                    name=perm_data["name"],
                    group=perm_data["group"],
                    description=perm_data.get("description"),
                    resource_type=perm_data.get("resource_type", "system"),
                )
                session.add(perm)
                new_perms += 1
        
        await session.flush()
        
        # Get all permissions for lookup
        perm_stmt = select(Permission)
        perm_result = await session.execute(perm_stmt)
        all_perms = {p.code: p for p in perm_result.scalars().all()}
        
        # Seed built-in system roles
        new_roles = 0
        for role_data in BUILTIN_ROLES:
            stmt = select(Role).where(Role.code == role_data["code"])
            result = await session.execute(stmt)
            existing = result.scalar_one_or_none()
            
            if existing:
                print(f"  系统角色已存在: {role_data['name']}")
                continue
            
            role = Role(
                name=role_data["name"],
                code=role_data["code"],
                scope=role_data["scope"],
                description=role_data["description"],
                is_builtin=True,
            )
            session.add(role)
            await session.flush()
            
            # Add permissions
            perm_count = 0
            for perm_code in role_data.get("permissions", []):
                if perm_code in all_perms:
                    rp = RolePermission(role_id=role.id, permission_id=all_perms[perm_code].id)
                    session.add(rp)
                    perm_count += 1
            
            print(f"  创建系统角色: {role_data['name']} ({perm_count} 个权限)")
            new_roles += 1
        
        # Seed built-in tenant roles (these are templates, not tied to specific tenants)
        for role_data in BUILTIN_TENANT_ROLES:
            # Tenant roles are created per-tenant, so we just print info
            print(f"  租户角色模板: {role_data['name']} ({len(role_data.get('permissions', []))} 个权限)")
        
        await session.commit()
        
        print(f"\n初始化完成: 新增 {new_perms} 个权限, {new_roles} 个角色")
    
    await engine.dispose()


if __name__ == "__main__":
    print("正在初始化权限和角色...")
    asyncio.run(init_permissions())
