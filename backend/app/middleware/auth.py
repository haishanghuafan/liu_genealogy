"""
Authentication middleware and dependencies
"""
from typing import Optional

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.security import verify_token
from app.models import User, Role, RolePermission, Permission, TenantUser


async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> Optional[User]:
    """Get current user from JWT token in request"""
    auth_header = request.headers.get("Authorization")
    
    if not auth_header:
        return None
    
    if not auth_header.startswith("Bearer "):
        return None
    
    token = auth_header.replace("Bearer ", "")
    
    user_id = verify_token(token)
    if not user_id:
        return None
    
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


async def get_user_permissions(
    user: User = Depends(get_current_user_required),
    db: AsyncSession = Depends(get_db),
) -> set[str]:
    """Get all permission codes for a user"""
    permissions = set()
    
    # Super admin has all permissions
    if user.is_super_admin:
        stmt = select(Permission.code)
        result = await db.execute(stmt)
        return set(result.scalars().all())
    
    # Get system-level role permissions
    system_role_stmt = (
        select(Permission.code)
        .join(RolePermission, RolePermission.permission_id == Permission.id)
        .join(Role, Role.id == RolePermission.role_id)
        .where(Role.scope == "system", Role.code == user.system_role)
    )
    system_result = await db.execute(system_role_stmt)
    permissions.update(system_result.scalars().all())
    
    return permissions


class PermissionChecker:
    """Permission checker dependency"""
    
    def __init__(self, *permissions: str, require_all: bool = False):
        self.permissions = set(permissions)
        self.require_all = require_all
    
    async def __call__(
        self,
        user: User = Depends(get_current_user_required),
        db: AsyncSession = Depends(get_db),
    ) -> User:
        # Super admin bypasses all permission checks
        if user.is_super_admin:
            return user
        
        # Get user's permissions
        user_perms = set()
        
        # System role permissions
        system_role_stmt = (
            select(Permission.code)
            .join(RolePermission, RolePermission.permission_id == Permission.id)
            .join(Role, Role.id == RolePermission.role_id)
            .where(Role.scope == "system", Role.code == user.system_role)
        )
        system_result = await db.execute(system_role_stmt)
        user_perms.update(system_result.scalars().all())
        
        # Check permissions
        if self.require_all:
            if not self.permissions.issubset(user_perms):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Missing permissions: {', '.join(self.permissions - user_perms)}",
                )
        else:
            if not self.permissions.intersection(user_perms):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions",
                )
        
        return user


class TenantPermissionChecker:
    """Check permissions within a specific tenant context"""
    
    def __init__(self, *permissions: str, require_all: bool = False):
        self.permissions = set(permissions)
        self.require_all = require_all
    
    async def __call__(
        self,
        user: User = Depends(get_current_user_required),
        db: AsyncSession = Depends(get_db),
        tenant_slug: str = None,
    ) -> User:
        # Super admin bypasses all permission checks
        if user.is_super_admin:
            return user
        
        if not tenant_slug:
            raise HTTPException(400, "Tenant slug required")
        
        # Get tenant
        from app.models import Tenant
        tenant_stmt = select(Tenant).where(Tenant.slug == tenant_slug)
        tenant_result = await db.execute(tenant_stmt)
        tenant = tenant_result.scalar_one_or_none()
        
        if not tenant:
            raise HTTPException(404, "Tenant not found")
        
        # Get user's tenant role
        tenant_user_stmt = select(TenantUser).where(
            TenantUser.user_id == user.id,
            TenantUser.tenant_id == tenant.id,
        )
        tenant_user_result = await db.execute(tenant_user_stmt)
        tenant_user = tenant_user_result.scalar_one_or_none()
        
        if not tenant_user:
            raise HTTPException(403, "Not a member of this tenant")
        
        # Get tenant role permissions
        role_stmt = (
            select(Permission.code)
            .join(RolePermission, RolePermission.permission_id == Permission.id)
            .join(Role, Role.id == RolePermission.role_id)
            .where(
                Role.scope == "tenant",
                Role.code == tenant_user.role,
                Role.tenant_id == tenant.id,
            )
        )
        role_result = await db.execute(role_stmt)
        user_perms = set(role_result.scalars().all())
        
        # Check permissions
        if self.require_all:
            if not self.permissions.issubset(user_perms):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Missing permissions: {', '.join(self.permissions - user_perms)}",
                )
        else:
            if not self.permissions.intersection(user_perms):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions",
                )
        
        return user


# Convenience dependencies
RequireAuth = Depends(get_current_user_required)
RequireSuperuser = Depends(get_superuser)
OptionalAuth = Depends(get_current_user)
