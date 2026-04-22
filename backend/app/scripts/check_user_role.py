"""
Check and fix user role

Usage:
    cd backend
    .\venv\Scripts\python.exe -m app.scripts.check_user_role admin@liushipu.com
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.core.config import settings
from app.models.system import User


async def check_user_role(email: str):
    """Check and optionally fix user role"""
    engine = create_async_engine(settings.database_url, echo=False)
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    
    async with async_session() as session:
        stmt = select(User).where(User.email == email)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user:
            print(f"用户 {email} 不存在")
            return
        
        print(f"用户信息:")
        print(f"  邮箱: {user.email}")
        print(f"  昵称: {user.nickname}")
        print(f"  角色: {user.system_role}")
        print(f"  状态: {'活跃' if user.is_active else '禁用'}")
        print(f"  是否超级管理员: {user.is_super_admin}")
        
        if user.system_role not in ("user", "operator", "super_admin"):
            print(f"\n角色值异常: '{user.system_role}'")
            fix = input("是否修复为 'user'? (y/n): ")
            if fix.lower() == "y":
                user.system_role = "user"
                await session.commit()
                print("已修复为 'user'")
        else:
            print("\n角色值正常")
        
        print(f"\n可设置为超级管理员?")
        upgrade = input("是否升级为超级管理员? (y/n): ")
        if upgrade.lower() == "y":
            user.system_role = "super_admin"
            await session.commit()
            print("已升级为超级管理员!")
    
    await engine.dispose()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python check_user_role.py <邮箱>")
        print("示例: python check_user_role.py admin@liushipu.com")
        sys.exit(1)
    
    email = sys.argv[1]
    asyncio.run(check_user_role(email))
