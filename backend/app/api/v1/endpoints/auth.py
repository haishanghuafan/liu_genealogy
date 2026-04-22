"""
Authentication endpoints
"""
from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import (
    create_access_token,
    create_refresh_token,
    get_password_hash,
    verify_password,
    verify_token,
)
from app.middleware.auth import get_current_user_required, get_superuser
from app.models import User

router = APIRouter(prefix="/auth", tags=["Authentication"])


# Schemas
class UserRegister(BaseModel):
    email: EmailStr
    password: str
    nickname: str | None = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: str
    email: str
    nickname: str | None
    avatar: str | None
    system_role: str
    
    class Config:
        from_attributes = True


# Endpoints
@router.post("/register", response_model=UserResponse)
async def register(
    data: UserRegister,
    db: AsyncSession = Depends(get_db),
):
    """Register a new user"""
    # Check if email already exists
    stmt = select(User).where(User.email == data.email)
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    
    # Create user
    user = User(
        email=data.email,
        password_hash=get_password_hash(data.password),
        nickname=data.nickname,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    return UserResponse(
        id=str(user.id),
        email=user.email,
        nickname=user.nickname,
        avatar=user.avatar,
        system_role=user.system_role,
    )


@router.post("/login", response_model=Token)
async def login(
    data: UserLogin,
    db: AsyncSession = Depends(get_db),
):
    """Login and get tokens"""
    # Find user
    stmt = select(User).where(User.email == data.email)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled",
        )
    
    # Update last login
    user.last_login_at = datetime.now(timezone.utc)
    await db.commit()
    
    # Create tokens
    access_token = create_access_token(subject=user.id)
    refresh_token = create_refresh_token(subject=user.id)
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
    )


class ChangePassword(BaseModel):
    old_password: str
    new_password: str


@router.post("/change-password", response_model=dict)
async def change_password(
    data: ChangePassword,
    db: AsyncSession = Depends(get_db),
    user = Depends(verify_token),
):
    """Change user password"""
    from uuid import UUID
    
    # Find user
    stmt = select(User).where(User.id == UUID(user))
    result = await db.execute(stmt)
    current_user = result.scalar_one_or_none()
    
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    # Verify old password
    if not verify_password(data.old_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid old password",
        )
    
    # Validate new password
    if len(data.new_password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be at least 6 characters",
        )
    
    # Update password
    current_user.password_hash = get_password_hash(data.new_password)
    await db.commit()
    
    return {"success": True, "message": "Password changed successfully"}


@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_token: str,
    db: AsyncSession = Depends(get_db),
):
    """Refresh access token"""
    user_id = verify_token(refresh_token, token_type="refresh")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )
    
    # Find user
    from uuid import UUID
    stmt = select(User).where(User.id == UUID(user_id))
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )
    
    # Create new tokens
    new_access_token = create_access_token(subject=user.id)
    new_refresh_token = create_refresh_token(subject=user.id)
    
    return Token(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    user: User = Depends(get_current_user_required),
):
    """Get current user info"""
    return UserResponse(
        id=str(user.id),
        email=user.email,
        nickname=user.nickname,
        avatar=user.avatar,
        system_role=user.system_role,
    )


# ============ Admin Endpoints ============

class AdminUserResponse(BaseModel):
    id: str
    email: str
    nickname: str | None
    avatar: str | None
    system_role: str
    is_active: bool
    email_verified: bool
    created_at: str
    last_login_at: str | None
    
    class Config:
        from_attributes = True


class AdminUserUpdate(BaseModel):
    nickname: str | None = None
    system_role: str | None = None
    is_active: bool | None = None


@router.get("/admin/users", response_model=dict)
async def admin_list_users(
    _admin=Depends(get_superuser),
    db: AsyncSession = Depends(get_db),
):
    """Admin: List all users"""
    stmt = select(User).order_by(User.created_at.desc())
    result = await db.execute(stmt)
    users = result.scalars().all()
    
    return {
        "success": True,
        "data": [
            {
                "id": str(u.id),
                "email": u.email,
                "nickname": u.nickname,
                "avatar": u.avatar,
                "system_role": u.system_role,
                "is_active": u.is_active,
                "email_verified": u.email_verified,
                "created_at": u.created_at.isoformat() if u.created_at else None,
                "last_login_at": u.last_login_at.isoformat() if u.last_login_at else None,
            }
            for u in users
        ],
    }


@router.put("/admin/users/{user_id}", response_model=dict)
async def admin_update_user(
    user_id: str,
    data: AdminUserUpdate,
    _admin=Depends(get_superuser),
    db: AsyncSession = Depends(get_db),
):
    """Admin: Update user"""
    from uuid import UUID
    
    stmt = select(User).where(User.id == UUID(user_id))
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(404, "User not found")
    
    updates = data.model_dump(exclude_unset=True)
    for key, value in updates.items():
        setattr(user, key, value)
    
    await db.commit()
    
    return {
        "success": True,
        "message": "用户已更新",
        "data": {
            "id": str(user.id),
            "email": user.email,
            "nickname": user.nickname,
            "system_role": user.system_role,
            "is_active": user.is_active,
        },
    }


@router.delete("/admin/users/{user_id}", response_model=dict)
async def admin_delete_user(
    user_id: str,
    _admin=Depends(get_superuser),
    db: AsyncSession = Depends(get_db),
):
    """Admin: Delete user"""
    from uuid import UUID
    
    stmt = select(User).where(User.id == UUID(user_id))
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(404, "User not found")
    
    if user.system_role == "super_admin":
        raise HTTPException(400, "Cannot delete super admin")
    
    await db.delete(user)
    await db.commit()
    
    return {"success": True, "message": "用户已删除"}
