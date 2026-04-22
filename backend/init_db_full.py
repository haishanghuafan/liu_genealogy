#!/usr/bin/env python3
"""
完整初始化数据库
"""
import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.core.config import settings
from app.models.system import Base as SystemBase, Tenant
from app.models.tenant import Base as TenantBase


async def init_database():
    """初始化数据库"""
    
    db_url = str(settings.database_url)
    print(f"数据库URL: {db_url}")
    
    # 创建引擎
    engine = create_async_engine(db_url, echo=False)
    
    # 创建系统表
    print("\n=== 创建系统表 ===")
    async with engine.begin() as conn:
        await conn.run_sync(SystemBase.metadata.create_all)
    print("系统表创建完成")
    
    # 创建租户
    print("\n=== 创建租户 ===")
    from sqlalchemy import select
    
    session_maker = async_sessionmaker(engine, expire_on_commit=False)
    
    async with session_maker() as db:
        # 检查租户是否存在
        result = await db.execute(select(Tenant).where(Tenant.slug == 'liushipu'))
        tenant = result.scalar_one_or_none()
        
        if not tenant:
            tenant = Tenant(
                slug='liushipu',
                name='liushipu家族',
                description='刘氏族谱管理系统',
                is_active=True,
                is_public=True
            )
            db.add(tenant)
            await db.commit()
            print(f"租户已创建: {tenant.id}")
        else:
            print(f"租户已存在: {tenant.id}")
    
    await engine.dispose()
    
    # 创建租户数据库
    print("\n=== 创建租户数据库 ===")
    import os
    db_dir = os.path.dirname(db_url.replace("sqlite+aiosqlite:///", ""))
    tenant_db_path = os.path.join(db_dir, "tenants", "liushipu.db")
    tenant_db_url = f"sqlite+aiosqlite:///{tenant_db_path}"
    
    print(f"租户数据库: {tenant_db_url}")
    
    # 创建新的租户引擎
    tenant_engine = create_async_engine(tenant_db_url, echo=False)
    
    # 创建租户表（如果不存在）
    async with tenant_engine.begin() as conn:
        await conn.run_sync(TenantBase.metadata.create_all)
    
    await tenant_engine.dispose()
    print("租户表创建/更新完成")
    
    print("\n=== 数据库初始化完成 ===")


if __name__ == "__main__":
    asyncio.run(init_database())
