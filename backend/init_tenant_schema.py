#!/usr/bin/env python3
"""
初始化租户数据库架构
"""
import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database import db_manager
from app.models.system import Tenant
from app.models.tenant import Base as TenantBase


async def init_tenant_schema():
    """初始化租户数据库架构"""
    
    # 获取系统数据库会话
    session_maker = db_manager.get_session_maker()
    
    async with session_maker() as db:
        # 获取租户信息
        from sqlalchemy import select
        result = await db.execute(select(Tenant).where(Tenant.slug == 'liushipu'))
        tenant = result.scalar_one_or_none()
        
        if not tenant:
            print("租户 liushipu 不存在，创建新租户...")
            tenant = Tenant(
                slug='liushipu',
                name='liushipu家族',
                description='刘氏族谱管理系统',
                status='active'
            )
            db.add(tenant)
            await db.commit()
            print(f"租户已创建: {tenant.id}")
        else:
            print(f"找到租户: {tenant.id}")
    
    # 创建租户表
    print("\n创建租户数据库表...")
    await db_manager.create_tenant_tables('liushipu')
    print("租户数据库表创建完成")


if __name__ == "__main__":
    asyncio.run(init_tenant_schema())
