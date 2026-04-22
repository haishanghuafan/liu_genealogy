"""
Permissions and roles management endpoints
"""
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.permissions import SYSTEM_PERMISSIONS, BUILTIN_ROLES, BUILTIN_TENANT_ROLES
from app.middleware.auth import get_superuser
from app.models import Permission, Role, RolePermission

router = APIRouter(prefix="/admin/permissions", tags=["Permissions & Roles"])


# ============ Schemas ============

class PermissionResponse(BaseModel):
    id: str
    code: str
    name: str
    group: str
    description: Optional[str]
    resource_type: str
    
    class Config:
        from_attributes = True


class RoleResponse(BaseModel):
    id: str
    name: str
    code: str
    scope: str
    tenant_id: Optional[str]
    description: Optional[str]
    is_builtin: bool
    permission_codes: list[str] = []
    
    class Config:
        from_attributes = True


class RoleCreate(BaseModel):
    name: str
    code: str
    scope: str = "system"
    tenant_id: Optional[str] = None
    description: Optional[str] = None
    permission_codes: list[str] = []


class RoleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    permission_codes: Optional[list[str]] = None


class RoleListResponse(BaseModel):
    id: str
    name: str
    code: str
    scope: str
    description: Optional[str]
    is_builtin: bool
    permission_count: int


# ============ Endpoints ============

@router.get("/list", response_model=dict)
async def list_all_permissions(
    scope: Optional[str] = None,
    tenant_id: Optional[str] = None,
    _admin=Depends(get_superuser),
    db: AsyncSession = Depends(get_db),
):
    """List permissions with tenant isolation support"""
    stmt = select(Permission).order_by(Permission.group, Permission.code)
    
    if scope == "system":
        # System-level permissions (no tenant)
        stmt = stmt.where(Permission.tenant_id.is_(None))
    elif scope == "tenant":
        # Tenant-level permissions
        if tenant_id:
            stmt = stmt.where(Permission.tenant_id == UUID(tenant_id))
        else:
            stmt = stmt.where(Permission.tenant_id.isnot(None))
    
    result = await db.execute(stmt)
    permissions = result.scalars().all()
    
    groups = {}
    for p in permissions:
        if p.group not in groups:
            groups[p.group] = []
        groups[p.group].append({
            "id": str(p.id),
            "code": p.code,
            "name": p.name,
            "description": p.description,
            "resource_type": p.resource_type,
            "tenant_id": str(p.tenant_id) if p.tenant_id else None,
        })
    
    return {
        "success": True,
        "data": {
            "groups": groups,
            "total": len(permissions),
            "scope": scope or "all",
        },
    }


@router.get("/roles", response_model=dict)
async def list_roles(
    scope: Optional[str] = None,
    tenant_id: Optional[str] = None,
    _admin=Depends(get_superuser),
    db: AsyncSession = Depends(get_db),
):
    """List all roles"""
    stmt = (
        select(Role)
        .options(
            selectinload(Role.permissions).selectinload(RolePermission.permission)
        )
        .order_by(Role.scope, Role.code)
    )
    
    if scope:
        stmt = stmt.where(Role.scope == scope)
    if tenant_id:
        stmt = stmt.where(Role.tenant_id == UUID(tenant_id))
    
    result = await db.execute(stmt)
    roles = result.scalars().all()
    
    return {
        "success": True,
        "data": [
            {
                "id": str(r.id),
                "name": r.name,
                "code": r.code,
                "scope": r.scope,
                "tenant_id": str(r.tenant_id) if r.tenant_id else None,
                "description": r.description,
                "is_builtin": r.is_builtin,
                "permission_count": len(r.permissions),
                "permission_codes": [p.permission.code for p in r.permissions],
            }
            for r in roles
        ],
    }


@router.get("/roles/{role_id}", response_model=dict)
async def get_role(
    role_id: str,
    _admin=Depends(get_superuser),
    db: AsyncSession = Depends(get_db),
):
    """Get role details"""
    stmt = (
        select(Role)
        .options(selectinload(Role.permissions).selectinload(RolePermission.permission))
        .where(Role.id == UUID(role_id))
    )
    result = await db.execute(stmt)
    role = result.scalar_one_or_none()
    
    if not role:
        raise HTTPException(404, "Role not found")
    
    return {
        "success": True,
        "data": {
            "id": str(role.id),
            "name": role.name,
            "code": role.code,
            "scope": role.scope,
            "tenant_id": str(role.tenant_id) if role.tenant_id else None,
            "description": role.description,
            "is_builtin": role.is_builtin,
            "permission_codes": [p.permission.code for p in role.permissions],
        },
    }


@router.post("/roles", response_model=dict)
async def create_role(
    data: RoleCreate,
    _admin=Depends(get_superuser),
    db: AsyncSession = Depends(get_db),
):
    """Create a new role with tenant isolation"""
    # Check if code already exists for this tenant
    tenant_uuid = UUID(data.tenant_id) if data.tenant_id else None
    stmt = select(Role).where(
        Role.code == data.code,
        Role.tenant_id == tenant_uuid
    )
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise HTTPException(400, "Role code already exists for this tenant")
    
    role = Role(
        name=data.name,
        code=data.code,
        scope=data.scope,
        tenant_id=tenant_uuid,
        description=data.description,
        is_builtin=False,
    )
    db.add(role)
    await db.flush()
    
    # Add permissions with tenant isolation
    if data.permission_codes:
        perm_stmt = select(Permission).where(Permission.code.in_(data.permission_codes))
        perm_result = await db.execute(perm_stmt)
        permissions = perm_result.scalars().all()
        
        for perm in permissions:
            rp = RolePermission(
                role_id=role.id, 
                permission_id=perm.id,
                tenant_id=tenant_uuid
            )
            db.add(rp)
    
    await db.commit()
    await db.refresh(role)
    
    return {
        "success": True,
        "message": "角色创建成功",
        "data": {
            "id": str(role.id),
            "code": role.code,
            "name": role.name,
            "tenant_id": data.tenant_id,
        },
    }


@router.put("/roles/{role_id}", response_model=dict)
async def update_role(
    role_id: str,
    data: RoleUpdate,
    _admin=Depends(get_superuser),
    db: AsyncSession = Depends(get_db),
):
    """Update role with tenant isolation"""
    stmt = select(Role).options(selectinload(Role.permissions).selectinload(RolePermission.permission)).where(Role.id == UUID(role_id))
    result = await db.execute(stmt)
    role = result.scalar_one_or_none()
    
    if not role:
        raise HTTPException(404, "Role not found")
    
    if role.is_builtin:
        raise HTTPException(400, "Cannot modify built-in role")
    
    updates = data.model_dump(exclude_unset=True)
    
    if "name" in updates:
        role.name = updates["name"]
    if "description" in updates:
        role.description = updates["description"]
    
    if "permission_codes" in updates:
        # Remove existing permissions for this role
        for rp in role.permissions:
            await db.delete(rp)
        
        # Add new permissions with tenant isolation
        if updates["permission_codes"]:
            perm_stmt = select(Permission).where(Permission.code.in_(updates["permission_codes"]))
            perm_result = await db.execute(perm_stmt)
            permissions = perm_result.scalars().all()
            
            for perm in permissions:
                rp = RolePermission(
                    role_id=role.id, 
                    permission_id=perm.id,
                    tenant_id=role.tenant_id
                )
                db.add(rp)
    
    await db.commit()
    
    return {
        "success": True,
        "message": "角色已更新",
        "data": {
            "id": str(role.id),
            "code": role.code,
            "name": role.name,
            "permission_codes": [p.permission.code for p in role.permissions],
        },
    }


@router.delete("/roles/{role_id}", response_model=dict)
async def delete_role(
    role_id: str,
    _admin=Depends(get_superuser),
    db: AsyncSession = Depends(get_db),
):
    """Delete role"""
    stmt = select(Role).where(Role.id == UUID(role_id))
    result = await db.execute(stmt)
    role = result.scalar_one_or_none()
    
    if not role:
        raise HTTPException(404, "Role not found")
    
    if role.is_builtin:
        raise HTTPException(400, "Cannot delete built-in role")
    
    await db.delete(role)
    await db.commit()
    
    return {"success": True, "message": "角色已删除"}


@router.post("/init", response_model=dict)
async def init_permissions(
    _admin=Depends(get_superuser),
    db: AsyncSession = Depends(get_db),
):
    """Initialize permissions and built-in roles"""
    # Seed permissions
    existing_codes = set()
    stmt = select(Permission.code)
    result = await db.execute(stmt)
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
            db.add(perm)
            new_perms += 1
    
    await db.flush()
    
    # Get all permissions for lookup
    perm_stmt = select(Permission)
    perm_result = await db.execute(perm_stmt)
    all_perms = {p.code: p for p in perm_result.scalars().all()}
    
    # Seed built-in system roles
    new_roles = 0
    for role_data in BUILTIN_ROLES:
        stmt = select(Role).where(Role.code == role_data["code"])
        result = await db.execute(stmt)
        existing = result.scalar_one_or_none()
        
        if existing:
            continue
        
        role = Role(
            name=role_data["name"],
            code=role_data["code"],
            scope=role_data["scope"],
            description=role_data["description"],
            is_builtin=True,
        )
        db.add(role)
        await db.flush()
        
        # Add permissions
        for perm_code in role_data.get("permissions", []):
            if perm_code in all_perms:
                rp = RolePermission(role_id=role.id, permission_id=all_perms[perm_code].id)
                db.add(rp)
        
        new_roles += 1
    
    # Seed built-in tenant roles
    for role_data in BUILTIN_TENANT_ROLES:
        stmt = select(Role).where(Role.code == role_data["code"])
        result = await db.execute(stmt)
        existing = result.scalar_one_or_none()
        
        if existing:
            continue
        
        role = Role(
            name=role_data["name"],
            code=role_data["code"],
            scope="tenant",
            description=role_data["description"],
            is_builtin=True,
        )
        db.add(role)
        await db.flush()
        
        # Add permissions
        for perm_code in role_data.get("permissions", []):
            if perm_code in all_perms:
                rp = RolePermission(role_id=role.id, permission_id=all_perms[perm_code].id)
                db.add(rp)
        
        new_roles += 1
    
    await db.commit()
    
    return {
        "success": True,
        "message": f"初始化完成: 新增 {new_perms} 个权限, {new_roles} 个角色",
        "data": {
            "new_permissions": new_perms,
            "new_roles": new_roles,
        },
    }
