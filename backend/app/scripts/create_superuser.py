"""
Create super admin user script

Usage:
    cd backend
    .\venv\Scripts\python.exe -m app.scripts.create_superuser admin@example.com YourPassword123
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from uuid import uuid4
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.core.config import settings
from app.core.security import get_password_hash
from app.models.system import User


async def create_superuser(email: str, password: str, nickname: str = "超级管理员"):
    """Create a super admin user"""
    engine = create_async_engine(settings.database_url, echo=False)
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    
    async with async_session() as session:
        from sqlalchemy import select
        stmt = select(User).where(User.email == email)
        result = await session.execute(stmt)
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            print(f"用户 {email} 已存在")
            if existing_user.system_role != "super_admin":
                print("正在升级为超级管理员...")
                existing_user.system_role = "super_admin"
                await session.commit()
                print("升级成功!")
            else:
                print("该用户已是超级管理员")
            return
        
        user = User(
            id=uuid4(),
            email=email,
            password_hash=get_password_hash(password),
            nickname=nickname,
            system_role="super_admin",
            is_active=True,
            email_verified=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        
        session.add(user)
        await session.commit()
        
        print(f"超级管理员创建成功!")
        print(f"邮箱: {email}")
        print(f"密码: {password}")
        print(f"\n请使用以上凭据登录系统")
    
    await engine.dispose()


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("用法: python create_superuser.py <邮箱> <密码> [昵称]")
        print("示例: python create_superuser.py admin@example.com Admin@123 管理员")
        sys.exit(1)
    
    email = sys.argv[1]
    password = sys.argv[2]
    nickname = sys.argv[3] if len(sys.argv) > 3 else "超级管理员"
    
    print(f"正在创建超级管理员...")
    asyncio.run(create_superuser(email, password, nickname))
