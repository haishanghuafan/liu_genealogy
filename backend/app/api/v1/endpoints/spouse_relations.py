"""
Spouse relations API endpoints
"""
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_tenant_db
from app.middleware.tenant import require_tenant
from app.models.tenant import SpouseRelation, Person
from app.services.family_service import FamilyService

router = APIRouter(prefix="/spouses", tags=["Spouse Relations"])


# ============ Schemas ============

class SpouseRelationCreate(BaseModel):
    """Schema for creating a spouse relation"""
    husband_id: str
    wife_id: str
    relation_type: str = Field("marriage", pattern="^(marriage|concubine|adopted|zhuazhui|first-fifth)$")
    sort_order: int = Field(1, ge=1)


class SpouseRelationUpdate(BaseModel):
    """Schema for updating a spouse relation"""
    relation_type: Optional[str] = Field(None, pattern="^(marriage|concubine|adopted|zhuazhui|first-fifth)$")
    sort_order: Optional[int] = Field(None, ge=1)


class SpouseRelationResponse(BaseModel):
    """Schema for spouse relation response"""
    id: str
    husband_id: str
    wife_id: str
    husband_name: Optional[str] = None
    wife_name: Optional[str] = None
    relation_type: str
    sort_order: int
    
    class Config:
        from_attributes = True


# ============ Endpoints ============

@router.get("/person/{person_id}", response_model=dict)
async def get_person_spouses(
    person_id: str,
    request: Request,
    db: AsyncSession = Depends(get_tenant_db),
):
    """Get all spouses of a person"""
    tenant = require_tenant(request)
    
    try:
        person_uuid = UUID(person_id)
    except ValueError:
        raise HTTPException(400, "Invalid person ID format")
    
    family_service = FamilyService(db)
    person = await family_service.get_person(person_uuid)
    
    if not person:
        raise HTTPException(404, "Person not found")
    
    spouses_data = await family_service.get_spouses(person)
    
    return {
        "success": True,
        "data": [
            {
                "id": str(s['spouse'].id),
                "name": s['spouse'].name,
                "gender": s['spouse'].gender,
                "relation_type": s['relation_type'],
                "order": s['order'],
            }
            for s in spouses_data
        ]
    }


@router.post("", response_model=dict)
async def create_spouse_relation(
    data: SpouseRelationCreate,
    request: Request,
    db: AsyncSession = Depends(get_tenant_db),
):
    """Create a new spouse relation"""
    tenant = require_tenant(request)
    
    # Validate husband
    try:
        husband_uuid = UUID(data.husband_id)
        husband = (await db.execute(
            select(Person).where(Person.id == husband_uuid)
        )).scalar_one_or_none()
        
        if not husband:
            raise HTTPException(400, "Husband not found")
        if husband.gender != 'M':
            raise HTTPException(400, "Husband must be male")
    except ValueError:
        raise HTTPException(400, "Invalid husband ID format")
    
    # Validate wife
    try:
        wife_uuid = UUID(data.wife_id)
        wife = (await db.execute(
            select(Person).where(Person.id == wife_uuid)
        )).scalar_one_or_none()
        
        if not wife:
            raise HTTPException(400, "Wife not found")
        if wife.gender != 'F':
            raise HTTPException(400, "Wife must be female")
    except ValueError:
        raise HTTPException(400, "Invalid wife ID format")
    
    # Check if relation already exists
    existing_stmt = select(SpouseRelation).where(
        SpouseRelation.husband_id == husband_uuid,
        SpouseRelation.wife_id == wife_uuid
    )
    result = await db.execute(existing_stmt)
    if result.scalar_one_or_none():
        raise HTTPException(400, "This spouse relation already exists")
    
    # Create relation
    relation = SpouseRelation(
        husband_id=husband_uuid,
        wife_id=wife_uuid,
        relation_type=data.relation_type,
        sort_order=data.sort_order,
    )
    db.add(relation)
    await db.commit()
    await db.refresh(relation)
    
    return {
        "success": True,
        "data": {"id": str(relation.id)}
    }


@router.put("/{relation_id}", response_model=dict)
async def update_spouse_relation(
    relation_id: str,
    data: SpouseRelationUpdate,
    request: Request,
    db: AsyncSession = Depends(get_tenant_db),
):
    """Update a spouse relation"""
    tenant = require_tenant(request)
    
    try:
        relation_uuid = UUID(relation_id)
    except ValueError:
        raise HTTPException(400, "Invalid relation ID format")
    
    stmt = select(SpouseRelation).where(SpouseRelation.id == relation_uuid)
    result = await db.execute(stmt)
    relation = result.scalar_one_or_none()
    
    if not relation:
        raise HTTPException(404, "Relation not found")
    
    # Update fields
    if data.relation_type is not None:
        relation.relation_type = data.relation_type
    if data.sort_order is not None:
        relation.sort_order = data.sort_order
    
    db.add(relation)
    await db.commit()
    await db.refresh(relation)
    
    return {
        "success": True,
        "message": "Relation updated successfully"
    }


@router.delete("/{relation_id}", response_model=dict)
async def delete_spouse_relation(
    relation_id: str,
    request: Request,
    db: AsyncSession = Depends(get_tenant_db),
):
    """Delete a spouse relation"""
    tenant = require_tenant(request)
    
    try:
        relation_uuid = UUID(relation_id)
    except ValueError:
        raise HTTPException(400, "Invalid relation ID format")
    
    stmt = select(SpouseRelation).where(SpouseRelation.id == relation_uuid)
    result = await db.execute(stmt)
    relation = result.scalar_one_or_none()
    
    if not relation:
        raise HTTPException(404, "Relation not found")
    
    await db.delete(relation)
    await db.commit()
    
    return {
        "success": True,
        "message": "Relation deleted successfully"
    }
