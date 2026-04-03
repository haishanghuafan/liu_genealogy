"""
Authentication middleware and dependencies
"""
from typing import Optional

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import verify_token
from app.models import User


async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> Optional[User]:
    """Get current user from JWT token in request"""
    # Try to get token from Authorization header
    auth_header = request.headers.get("Authorization")
    
    if not auth_header:
        return None
    
    if not auth_header.startswith("Bearer "):
        return None
    
    token = auth_header.replace("Bearer ", "")
    
    # Verify token
    user_id = verify_token(token)
    if not user_id:
        return None
    
    # Load user from database
    try:
        from uuid import UUID
        stmt = select(User).where(User.id == UUID(user_id))
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        return user
    except Exception:
        return None


async def get_current_user_required(
    user: Optional[User] = Depends(get_current_user),
) -> User:
    """Get current user, raise 401 if not authenticated"""
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def get_superuser(
    user: User = Depends(get_current_user_required),
) -> User:
    """Get current superuser, raise 403 if not superuser"""
    if not user.is_super_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Superuser access required",
        )
    return user


class PermissionChecker:
    """Permission checker dependency"""
    
    def __init__(self, permission: str):
        self.permission = permission
    
    def __call__(self, user: User = Depends(get_current_user_required)) -> User:
        # TODO: Implement actual permission checking
        # For now, just check if user is authenticated
        return user


# Convenience dependencies
RequireAuth = Depends(get_current_user_required)
RequireSuperuser = Depends(get_superuser)
OptionalAuth = Depends(get_current_user)
