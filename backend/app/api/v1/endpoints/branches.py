"""
Branch API endpoints - CRUD operations for family branches
"""
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_tenant_db
from app.middleware.tenant import require_tenant
from app.models.tenant import Branch, Person
from app.services.family_service import FamilyService

router = APIRouter(prefix="/branches", tags=["Branches"])


# ============ Schemas ============

class BranchBase(BaseModel):
    """Base branch fields"""
    name: str = Field(..., min_length=1, max_length=100)
    founder_id: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = Field(None, max_length=200)


class BranchCreate(BranchBase):
    """Schema for creating a branch"""
    pass


class BranchUpdate(BaseModel):
    """Schema for updating a branch"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    founder_id: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = Field(None, max_length=200)


class BranchResponse(BaseModel):
    """Schema for branch response"""
    id: str
    name: str
    founder_id: Optional[str] = None
    founder_name: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    member_count: int = 0
    created_at: datetime
    
    class Config:
        from_attributes = True


class BranchListResponse(BaseModel):
    success: bool = True
    data: list[BranchResponse]
    meta: dict


# ============ Endpoints ============

@router.get("", response_model=BranchListResponse)
async def list_branches(
    request: Request,
    db: AsyncSession = Depends(get_tenant_db),
):
    """List all branches"""
    tenant = require_tenant(request)
    
    stmt = select(Branch).order_by(Branch.name)
    result = await db.execute(stmt)
    branches = result.scalars().all()
    
    # Get member count for each branch
    branch_data = []
    for branch in branches:
        member_count = (await db.execute(
            select(func.count()).select_from(Person).where(Person.branch_id == branch.id)
        )).scalar()
        
        founder_name = None
        if branch.founder_id:
            founder = (await db.execute(
                select(Person).where(Person.id == branch.founder_id)
            )).scalar_one_or_none()
            if founder:
                founder_name = founder.name
        
        branch_data.append({
            "id": str(branch.id),
            "name": branch.name,
            "founder_id": str(branch.founder_id) if branch.founder_id else None,
            "founder_name": founder_name,
            "description": branch.description,
            "location": branch.location,
            "member_count": member_count,
            "created_at": branch.created_at,
        })
    
    return BranchListResponse(
        data=branch_data,
        meta={"total": len(branches)}
    )


@router.get("/{branch_id}", response_model=dict)
async def get_branch(
    branch_id: str,
    request: Request,
    db: AsyncSession = Depends(get_tenant_db),
):
    """Get branch details"""
    tenant = require_tenant(request)
    
    try:
        branch_uuid = UUID(branch_id)
    except ValueError:
        raise HTTPException(400, "Invalid branch ID format")
    
    stmt = select(Branch).where(Branch.id == branch_uuid)
    result = await db.execute(stmt)
    branch = result.scalar_one_or_none()
    
    if not branch:
        raise HTTPException(404, "Branch not found")
    
    # Get founder info
    founder_name = None
    if branch.founder_id:
        founder = (await db.execute(
            select(Person).where(Person.id == branch.founder_id)
        )).scalar_one_or_none()
        if founder:
            founder_name = founder.name
    
    # Get all members
    members_stmt = select(Person).where(Person.branch_id == branch_uuid).order_by(
        Person.sort_order, Person.id
    )
    result = await db.execute(members_stmt)
    members = result.scalars().all()
    
    return {
        "success": True,
        "data": {
            "id": str(branch.id),
            "name": branch.name,
            "founder_id": str(branch.founder_id) if branch.founder_id else None,
            "founder_name": founder_name,
            "description": branch.description,
            "location": branch.location,
            "members": [
                {
                    "id": str(m.id),
                    "name": m.name,
                    "generation_id": m.generation_id,
                    "gender": m.gender,
                    "birth_year": m.birth_year,
                    "death_year": m.death_year,
                }
                for m in members
            ],
            "member_count": len(members),
        }
    }


@router.post("", response_model=dict)
async def create_branch(
    data: BranchCreate,
    request: Request,
    db: AsyncSession = Depends(get_tenant_db),
):
    """Create a new branch"""
    tenant = require_tenant(request)
    
    # Validate founder if provided
    founder = None
    if data.founder_id:
        try:
            founder_uuid = UUID(data.founder_id)
            founder = (await db.execute(
                select(Person).where(Person.id == founder_uuid)
            )).scalar_one_or_none()
            if not founder:
                raise HTTPException(400, "Founder person not found")
        except ValueError:
            raise HTTPException(400, "Invalid founder ID format")
    
    branch = Branch(
        name=data.name,
        founder_id=founder.id if founder else None,
        description=data.description,
        location=data.location,
    )
    db.add(branch)
    await db.commit()
    await db.refresh(branch)
    
    return {
        "success": True,
        "data": {"id": str(branch.id), "name": branch.name}
    }


@router.put("/{branch_id}", response_model=dict)
async def update_branch(
    branch_id: str,
    data: BranchUpdate,
    request: Request,
    db: AsyncSession = Depends(get_tenant_db),
):
    """Update a branch"""
    tenant = require_tenant(request)
    
    try:
        branch_uuid = UUID(branch_id)
    except ValueError:
        raise HTTPException(400, "Invalid branch ID format")
    
    stmt = select(Branch).where(Branch.id == branch_uuid)
    result = await db.execute(stmt)
    branch = result.scalar_one_or_none()
    
    if not branch:
        raise HTTPException(404, "Branch not found")
    
    # Update fields
    if data.name is not None:
        branch.name = data.name
    if data.founder_id is not None:
        try:
            founder_uuid = UUID(data.founder_id)
            founder = (await db.execute(
                select(Person).where(Person.id == founder_uuid)
            )).scalar_one_or_none()
            if not founder:
                raise HTTPException(400, "Founder person not found")
            branch.founder_id = founder.id
        except ValueError:
            raise HTTPException(400, "Invalid founder ID format")
    if data.description is not None:
        branch.description = data.description
    if data.location is not None:
        branch.location = data.location
    
    db.add(branch)
    await db.commit()
    await db.refresh(branch)
    
    return {
        "success": True,
        "message": "Branch updated successfully"
    }


@router.delete("/{branch_id}", response_model=dict)
async def delete_branch(
    branch_id: str,
    request: Request,
    db: AsyncSession = Depends(get_tenant_db),
):
    """Delete a branch"""
    tenant = require_tenant(request)
    
    try:
        branch_uuid = UUID(branch_id)
    except ValueError:
        raise HTTPException(400, "Invalid branch ID format")
    
    stmt = select(Branch).where(Branch.id == branch_uuid)
    result = await db.execute(stmt)
    branch = result.scalar_one_or_none()
    
    if not branch:
        raise HTTPException(404, "Branch not found")
    
    # Check if branch has members
    member_count = (await db.execute(
        select(func.count()).select_from(Person).where(Person.branch_id == branch_uuid)
    )).scalar()
    
    if member_count > 0:
        raise HTTPException(
            400, 
            f"Cannot delete branch with {member_count} members. Please reassign members first."
        )
    
    await db.delete(branch)
    await db.commit()
    
    return {
        "success": True,
        "message": "Branch deleted successfully"
    }
