"""
Member management endpoints - invite, manage tenant members
"""
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel, Field
from sqlalchemy import func, select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.plans import get_plan_features
from app.middleware.tenant import require_tenant
from app.middleware.auth import get_current_user_required
from app.models.system import TenantUser, User
from app.services.quota_service import quota_service, format_quota_error

router = APIRouter(prefix="/members", tags=["Members"])


# ============ Schemas ============

class MemberInvite(BaseModel):
    """Invite a user to tenant"""
    email: str = Field(..., description="Email of user to invite")
    role: str = Field("member", pattern="^(guest|member|editor|reviewer|tenant_admin)$")
    person_id: Optional[str] = Field(None, description="Link to a genealogy person")


class MemberRoleUpdate(BaseModel):
    """Update member role"""
    role: str = Field(..., pattern="^(guest|member|editor|reviewer|tenant_admin)$")


class MemberResponse(BaseModel):
    """Member info response"""
    id: str
    user_id: str
    email: str
    nickname: Optional[str]
    avatar: Optional[str]
    role: str
    person_id: Optional[str]
    joined_at: str
    invited_by: Optional[str]


class MemberListResponse(BaseModel):
    success: bool = True
    data: list[MemberResponse]
    meta: dict


# ============ Helper ============

ROLE_DISPLAY = {
    "guest": "受邀访客",
    "member": "家族成员",
    "editor": "编辑人员",
    "reviewer": "审核人员",
    "tenant_admin": "家族管理员",
}


async def _require_admin(
    request: Request,
    db: AsyncSession,
    user: User,
    tenant_id: UUID,
) -> TenantUser:
    """Verify user is tenant admin and return TenantUser record"""
    stmt = select(TenantUser).where(
        and_(
            TenantUser.user_id == user.id,
            TenantUser.tenant_id == tenant_id,
            TenantUser.role == "tenant_admin",
        )
    )
    result = await db.execute(stmt)
    tu = result.scalar_one_or_none()
    if not tu:
        raise HTTPException(403, "需要家族管理员权限")
    return tu


# ============ Endpoints ============

@router.get("", response_model=MemberListResponse)
async def list_members(
    request: Request,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    role: Optional[str] = Query(None, pattern="^(guest|member|editor|reviewer|tenant_admin)$"),
    db: AsyncSession = Depends(get_db),
):
    """List all members of current tenant"""
    tenant = require_tenant(request)
    
    query = select(TenantUser).where(TenantUser.tenant_id == tenant.id)
    
    if role:
        query = query.where(TenantUser.role == role)
    
    # Count
    count_stmt = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_stmt)).scalar()
    
    # Paginate
    query = query.offset((page - 1) * page_size).limit(page_size)
    query = query.order_by(TenantUser.joined_at.desc())
    
    result = await db.execute(query)
    members = result.scalars().all()
    
    data = []
    for m in members:
        # Fetch user info
        user_stmt = select(User).where(User.id == m.user_id)
        user_result = await db.execute(user_stmt)
        user = user_result.scalar_one_or_none()
        
        data.append({
            "id": str(m.id),
            "user_id": str(m.user_id),
            "email": user.email if user else None,
            "nickname": user.nickname if user else None,
            "avatar": user.avatar if user else None,
            "role": m.role,
            "person_id": str(m.person_id) if m.person_id else None,
            "joined_at": m.joined_at.isoformat(),
            "invited_by": str(m.invited_by) if m.invited_by else None,
        })
    
    return MemberListResponse(
        data=data,
        meta={
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size if total else 0,
        },
    )


@router.post("/invite", response_model=dict, status_code=201)
async def invite_member(
    data: MemberInvite,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user_required),
):
    """Invite a user to tenant (admin only)"""
    tenant = require_tenant(request)
    await _require_admin(request, db, user, tenant.id)
    
    # Check member quota
    members_stmt = select(func.count()).select_from(TenantUser).where(
        TenantUser.tenant_id == tenant.id
    )
    current_members = (await db.execute(members_stmt)).scalar() or 0
    
    quota_result = await quota_service.check_members_quota(tenant.plan, current_members)
    if not quota_result.allowed:
        raise HTTPException(403, format_quota_error(quota_result))
    
    # If assigning admin role, check admin quota
    if data.role == "tenant_admin":
        admins_stmt = select(func.count()).select_from(TenantUser).where(
            and_(
                TenantUser.tenant_id == tenant.id,
                TenantUser.role == "tenant_admin",
            )
        )
        current_admins = (await db.execute(admins_stmt)).scalar() or 0
        
        admin_quota = await quota_service.check_admins_quota(tenant.plan, current_admins)
        if not admin_quota.allowed:
            raise HTTPException(403, format_quota_error(admin_quota))
    
    # Find or check user by email
    user_stmt = select(User).where(User.email == data.email)
    user_result = await db.execute(user_stmt)
    target_user = user_result.scalar_one_or_none()
    
    if not target_user:
        raise HTTPException(404, f"用户 {data.email} 不存在，请先邀请注册")
    
    # Check if already a member
    existing_stmt = select(TenantUser).where(
        and_(
            TenantUser.user_id == target_user.id,
            TenantUser.tenant_id == tenant.id,
        )
    )
    existing = (await db.execute(existing_stmt)).scalar_one_or_none()
    if existing:
        raise HTTPException(400, f"{data.email} 已是本家族成员")
    
    # Create membership
    person_id = UUID(data.person_id) if data.person_id else None
    
    membership = TenantUser(
        user_id=target_user.id,
        tenant_id=tenant.id,
        role=data.role,
        person_id=person_id,
        invited_by=user.id,
    )
    db.add(membership)
    await db.commit()
    
    return {
        "success": True,
        "message": f"已邀请 {data.email} ({ROLE_DISPLAY.get(data.role, data.role)})",
        "data": {
            "id": str(membership.id),
            "email": data.email,
            "role": data.role,
        },
    }


@router.put("/{member_id}/role", response_model=dict)
async def update_member_role(
    member_id: str,
    data: MemberRoleUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user_required),
):
    """Update member role (admin only)"""
    tenant = require_tenant(request)
    await _require_admin(request, db, user, tenant.id)
    
    # If promoting to admin, check quota
    if data.role == "tenant_admin":
        admins_stmt = select(func.count()).select_from(TenantUser).where(
            and_(
                TenantUser.tenant_id == tenant.id,
                TenantUser.role == "tenant_admin",
            )
        )
        current_admins = (await db.execute(admins_stmt)).scalar() or 0
        
        admin_quota = await quota_service.check_admins_quota(tenant.plan, current_admins)
        if not admin_quota.allowed:
            raise HTTPException(403, format_quota_error(admin_quota))
    
    # Find member
    stmt = select(TenantUser).where(
        and_(
            TenantUser.id == UUID(member_id),
            TenantUser.tenant_id == tenant.id,
        )
    )
    result = await db.execute(stmt)
    membership = result.scalar_one_or_none()
    
    if not membership:
        raise HTTPException(404, "成员不存在")
    
    old_role = membership.role
    membership.role = data.role
    await db.commit()
    
    return {
        "success": True,
        "message": f"角色已从 {ROLE_DISPLAY.get(old_role, old_role)} 更新为 {ROLE_DISPLAY.get(data.role, data.role)}",
    }


@router.delete("/{member_id}", response_model=dict)
async def remove_member(
    member_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user_required),
):
    """Remove member from tenant (admin only)"""
    tenant = require_tenant(request)
    await _require_admin(request, db, user, tenant.id)
    
    # Find member
    stmt = select(TenantUser).where(
        and_(
            TenantUser.id == UUID(member_id),
            TenantUser.tenant_id == tenant.id,
        )
    )
    result = await db.execute(stmt)
    membership = result.scalar_one_or_none()
    
    if not membership:
        raise HTTPException(404, "成员不存在")
    
    # Don't allow removing yourself
    if membership.user_id == user.id:
        raise HTTPException(400, "不能移除自己，请转让管理员后再退出")
    
    # Get user email for response
    user_stmt = select(User).where(User.id == membership.user_id)
    target_user = (await db.execute(user_stmt)).scalar_one_or_none()
    
    await db.delete(membership)
    await db.commit()
    
    return {
        "success": True,
        "message": f"已移除成员 {target_user.email if target_user else member_id}",
    }


@router.get("/me", response_model=dict)
async def get_my_membership(
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user_required),
):
    """Get current user's membership in tenant"""
    tenant = require_tenant(request)
    
    stmt = select(TenantUser).where(
        and_(
            TenantUser.user_id == user.id,
            TenantUser.tenant_id == tenant.id,
        )
    )
    result = await db.execute(stmt)
    membership = result.scalar_one_or_none()
    
    if not membership:
        raise HTTPException(404, "您不是本家族的成员")
    
    return {
        "success": True,
        "data": {
            "id": str(membership.id),
            "role": membership.role,
            "role_display": ROLE_DISPLAY.get(membership.role, membership.role),
            "person_id": str(membership.person_id) if membership.person_id else None,
            "joined_at": membership.joined_at.isoformat(),
            "permissions": _get_role_permissions(membership.role),
        },
    }


def _get_role_permissions(role: str) -> list[str]:
    """Get permission list for a role"""
    perms = {
        "guest": ["view_public", "search_basic", "search_advanced"],
        "member": ["view_public", "search_basic", "search_advanced", "view_persons"],
        "editor": [
            "view_public", "search_basic", "search_advanced", "view_persons",
            "create_person", "edit_person", "manage_media",
        ],
        "reviewer": [
            "view_public", "search_basic", "search_advanced", "view_persons",
            "create_person", "edit_person", "manage_media", "approve_changes",
        ],
        "tenant_admin": [
            "view_public", "view_private", "search_basic", "search_advanced",
            "view_persons", "create_person", "edit_person", "delete_person",
            "manage_media", "approve_changes", "manage_members", "manage_tenant",
        ],
    }
    return perms.get(role, [])
