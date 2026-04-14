"""
Generation API endpoints - CRUD operations for generations
"""
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_tenant_db
from app.middleware.tenant import require_tenant
from app.models.tenant import Generation, Person
from app.services.family_service import FamilyService

router = APIRouter(prefix="/generations", tags=["Generations"])


# ============ Schemas ============

class GenerationBase(BaseModel):
    """Base generation fields"""
    number: int = Field(..., ge=1, le=100)
    is_spouse: bool = False
    name: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = None


class GenerationCreate(GenerationBase):
    """Schema for creating a generation"""
    pass


class GenerationUpdate(BaseModel):
    """Schema for updating a generation"""
    number: Optional[int] = Field(None, ge=1, le=100)
    is_spouse: Optional[bool] = None
    name: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = None


class GenerationResponse(BaseModel):
    """Schema for generation response"""
    id: int
    number: int
    is_spouse: bool
    name: Optional[str] = None
    description: Optional[str] = None
    person_count: int = 0
    title: str = ""
    
    class Config:
        from_attributes = True


class GenerationListResponse(BaseModel):
    success: bool = True
    data: list[GenerationResponse]
    meta: dict


# ============ Endpoints ============

@router.get("", response_model=GenerationListResponse)
async def list_generations(
    request: Request,
    db: AsyncSession = Depends(get_tenant_db),
):
    """List all generations"""
    tenant = require_tenant(request)
    
    # Get all generations, ordered by number
    stmt = select(Generation).order_by(Generation.number, Generation.is_spouse)
    result = await db.execute(stmt)
    generations = result.scalars().all()
    
    # Get person count and title for each generation
    family_service = FamilyService(db)
    gen_data = []
    
    for gen in generations:
        person_count = (await db.execute(
            select(func.count()).select_from(Person).where(Person.generation_id == gen.id)
        )).scalar()
        
        title = await family_service.get_generation_title(gen.id)
        
        gen_data.append({
            "id": gen.id,
            "number": gen.number,
            "is_spouse": gen.is_spouse,
            "name": gen.name,
            "description": gen.description,
            "person_count": person_count,
            "title": title,
        })
    
    return GenerationListResponse(
        data=gen_data,
        meta={"total": len(generations)}
    )


@router.get("/{generation_id}", response_model=dict)
async def get_generation(
    generation_id: int,
    request: Request,
    db: AsyncSession = Depends(get_tenant_db),
):
    """Get generation details"""
    tenant = require_tenant(request)
    
    stmt = select(Generation).where(Generation.id == generation_id)
    result = await db.execute(stmt)
    generation = result.scalar_one_or_none()
    
    if not generation:
        raise HTTPException(404, "Generation not found")
    
    # Get all persons in this generation
    persons_stmt = select(Person).where(
        Person.generation_id == generation_id
    ).order_by(Person.sort_order, Person.id)
    
    result = await db.execute(persons_stmt)
    persons = result.scalars().all()
    
    family_service = FamilyService(db)
    title = await family_service.get_generation_title(generation_id)
    
    return {
        "success": True,
        "data": {
            "id": generation.id,
            "number": generation.number,
            "is_spouse": generation.is_spouse,
            "name": generation.name,
            "description": generation.description,
            "title": title,
            "persons": [
                {
                    "id": str(p.id),
                    "name": p.name,
                    "gender": p.gender,
                    "birth_year": p.birth_year,
                    "death_year": p.death_year,
                    "branch_id": str(p.branch_id) if p.branch_id else None,
                }
                for p in persons
            ],
            "person_count": len(persons),
        }
    }


@router.post("", response_model=dict)
async def create_generation(
    data: GenerationCreate,
    request: Request,
    db: AsyncSession = Depends(get_tenant_db),
):
    """Create a new generation"""
    tenant = require_tenant(request)
    
    # Check if this generation number already exists
    stmt = select(Generation).where(
        Generation.number == data.number,
        Generation.is_spouse == data.is_spouse
    )
    result = await db.execute(stmt)
    existing = result.scalar_one_or_none()
    
    if existing:
        raise HTTPException(
            400, 
            f"Generation {data.number}{' (spouse)' if data.is_spouse else ''} already exists"
        )
    
    generation = Generation(
        number=data.number,
        is_spouse=data.is_spouse,
        name=data.name,
        description=data.description,
    )
    db.add(generation)
    await db.commit()
    await db.refresh(generation)
    
    return {
        "success": True,
        "data": {"id": generation.id, "number": generation.number}
    }


@router.put("/{generation_id}", response_model=dict)
async def update_generation(
    generation_id: int,
    data: GenerationUpdate,
    request: Request,
    db: AsyncSession = Depends(get_tenant_db),
):
    """Update a generation"""
    tenant = require_tenant(request)
    
    stmt = select(Generation).where(Generation.id == generation_id)
    result = await db.execute(stmt)
    generation = result.scalar_one_or_none()
    
    if not generation:
        raise HTTPException(404, "Generation not found")
    
    # Check for conflicts if changing number
    if data.number is not None and data.number != generation.number:
        is_spouse = data.is_spouse if data.is_spouse is not None else generation.is_spouse
        conflict_stmt = select(Generation).where(
            Generation.number == data.number,
            Generation.is_spouse == is_spouse,
            Generation.id != generation_id
        )
        conflict_result = await db.execute(conflict_stmt)
        if conflict_result.scalar_one_or_none():
            raise HTTPException(
                400, 
                f"Generation {data.number}{' (spouse)' if is_spouse else ''} already exists"
            )
    
    # Update fields
    if data.number is not None:
        generation.number = data.number
    if data.is_spouse is not None:
        generation.is_spouse = data.is_spouse
    if data.name is not None:
        generation.name = data.name
    if data.description is not None:
        generation.description = data.description
    
    db.add(generation)
    await db.commit()
    await db.refresh(generation)
    
    return {
        "success": True,
        "message": "Generation updated successfully"
    }


@router.delete("/{generation_id}", response_model=dict)
async def delete_generation(
    generation_id: int,
    request: Request,
    db: AsyncSession = Depends(get_tenant_db),
):
    """Delete a generation"""
    tenant = require_tenant(request)
    
    stmt = select(Generation).where(Generation.id == generation_id)
    result = await db.execute(stmt)
    generation = result.scalar_one_or_none()
    
    if not generation:
        raise HTTPException(404, "Generation not found")
    
    # Check if generation has persons
    person_count = (await db.execute(
        select(func.count()).select_from(Person).where(Person.generation_id == generation_id)
    )).scalar()
    
    if person_count > 0:
        raise HTTPException(
            400, 
            f"Cannot delete generation with {person_count} persons. Please reassign persons first."
        )
    
    await db.delete(generation)
    await db.commit()
    
    return {
        "success": True,
        "message": "Generation deleted successfully"
    }


@router.get("/title/{generation_id}", response_model=dict)
async def get_generation_title(
    generation_id: int,
    request: Request,
    db: AsyncSession = Depends(get_tenant_db),
):
    """Get traditional Chinese title for a generation"""
    tenant = require_tenant(request)
    
    family_service = FamilyService(db)
    title = await family_service.get_generation_title(generation_id)
    
    return {
        "success": True,
        "data": {"title": title}
    }
