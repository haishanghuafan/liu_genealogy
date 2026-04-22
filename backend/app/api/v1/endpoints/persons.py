"""
Person API endpoints - CRUD operations
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
from app.models.tenant import Person, Generation, Branch, SpouseRelation
from app.services.quota_service import quota_service, format_quota_error

router = APIRouter(prefix="/persons", tags=["Persons"])


# ============ Schemas ============

class PersonBase(BaseModel):
    """Base person fields"""
    name: str = Field(..., min_length=1, max_length=100)
    courtesy_name: Optional[str] = Field(None, max_length=100)
    art_name: Optional[str] = Field(None, max_length=100)
    alias: Optional[str] = Field(None, max_length=100)
    generation_char: Optional[str] = Field(None, max_length=10)
    gender: str = Field("M", pattern="^(M|F)$")
    is_outsider: bool = False
    
    generation_id: Optional[int] = None
    branch_id: Optional[UUID] = None
    branch_name: Optional[str] = Field(None, max_length=100)
    branch_generation_name: Optional[str] = Field(None, max_length=100)
    
    father_id: Optional[UUID] = None
    mother_id: Optional[UUID] = None
    
    birth_year: Optional[int] = Field(None, ge=0, le=2100)
    death_year: Optional[int] = Field(None, ge=0, le=2100)
    birth_place: Optional[str] = Field(None, max_length=200)
    lunar_birthday: Optional[str] = Field(None, max_length=50)
    
    burial_place: Optional[str] = Field(None, max_length=300)
    burial_fengshui: Optional[str] = Field(None, max_length=200)
    burial_direction: Optional[str] = Field(None, max_length=100)
    
    biography: Optional[str] = None
    achievements: Optional[str] = None
    descendants_location: Optional[str] = None
    notes: Optional[str] = None
    
    visibility: str = Field("public", pattern="^(public|member|private)$")
    sort_order: int = 0


class PersonCreate(PersonBase):
    """Schema for creating a person"""
    pass


class PersonUpdate(BaseModel):
    """Schema for updating a person - all fields optional"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    courtesy_name: Optional[str] = Field(None, max_length=100)
    art_name: Optional[str] = Field(None, max_length=100)
    alias: Optional[str] = Field(None, max_length=100)
    generation_char: Optional[str] = Field(None, max_length=10)
    gender: Optional[str] = Field(None, pattern="^(M|F)$")
    is_outsider: Optional[bool] = None
    
    generation_id: Optional[int] = None
    branch_id: Optional[UUID] = None
    branch_name: Optional[str] = Field(None, max_length=100)
    branch_generation_name: Optional[str] = Field(None, max_length=100)
    
    father_id: Optional[UUID] = None
    mother_id: Optional[UUID] = None
    
    birth_year: Optional[int] = Field(None, ge=0, le=2100)
    death_year: Optional[int] = Field(None, ge=0, le=2100)
    birth_place: Optional[str] = Field(None, max_length=200)
    lunar_birthday: Optional[str] = Field(None, max_length=50)
    
    burial_place: Optional[str] = Field(None, max_length=300)
    burial_fengshui: Optional[str] = Field(None, max_length=200)
    burial_direction: Optional[str] = Field(None, max_length=100)
    
    biography: Optional[str] = None
    achievements: Optional[str] = None
    descendants_location: Optional[str] = None
    notes: Optional[str] = None
    
    visibility: Optional[str] = Field(None, pattern="^(public|member|private)$")
    sort_order: Optional[int] = None


class PersonResponse(BaseModel):
    """Schema for person response"""
    id: str
    name: str
    courtesy_name: Optional[str] = None
    art_name: Optional[str] = None
    alias: Optional[str] = None
    generation_char: Optional[str] = None
    gender: str
    is_outsider: bool
    
    generation_id: Optional[int] = None
    branch_id: Optional[str] = None
    branch_name: Optional[str] = None
    branch_generation_name: Optional[str] = None
    
    father_id: Optional[str] = None
    mother_id: Optional[str] = None
    
    birth_year: Optional[int] = None
    death_year: Optional[int] = None
    birth_place: Optional[str] = None
    lunar_birthday: Optional[str] = None
    
    burial_place: Optional[str] = None
    burial_fengshui: Optional[str] = None
    burial_direction: Optional[str] = None
    
    biography: Optional[str] = None
    achievements: Optional[str] = None
    descendants_location: Optional[str] = None
    notes: Optional[str] = None
    
    visibility: str
    sort_order: int
    avatar: Optional[str] = None
    
    created_at: datetime
    updated_at: datetime
    
    # Computed fields
    full_name: Optional[str] = None
    generation_name: Optional[str] = None
    computed_branch_name: Optional[str] = None
    father_name: Optional[str] = None
    mother_name: Optional[str] = None
    
    class Config:
        from_attributes = True


class PersonListResponse(BaseModel):
    success: bool = True
    data: list[PersonResponse]
    meta: dict


class SpouseRelationCreate(BaseModel):
    """Schema for creating spouse relation"""
    husband_id: UUID
    wife_id: UUID
    # Relation type - traditional Chinese genealogy types
    # marriage: 正室, concubine: 妾室, adopted: 继配
    # zhuazhui: 招赘, first-fifth: 一至五房
    relation_type: str = Field("marriage", pattern="^(marriage|concubine|adopted|zhuazhui|first|second|third|fourth|fifth)$")
    source_info: Optional[str] = Field(None, max_length=200)
    sort_order: int = 1


class SpouseRelationResponse(BaseModel):
    id: str
    husband_id: str
    wife_id: str
    husband_name: Optional[str] = None
    wife_name: Optional[str] = None
    relation_type: str
    source_info: Optional[str] = None
    sort_order: int


# ============ Endpoints ============

@router.get("", response_model=PersonListResponse)
async def list_persons(
    request: Request,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    generation: Optional[int] = Query(None),
    branch_id: Optional[str] = Query(None),
    gender: Optional[str] = Query(None, pattern="^(M|F)$"),
    search: Optional[str] = Query(None, max_length=100),
    visibility: Optional[str] = Query(None, pattern="^(public|member|private)$"),
    db: AsyncSession = Depends(get_tenant_db),
):
    """List persons with filters and pagination"""
    require_tenant(request)
    
    # Build query
    query = select(Person)
    
    # Apply filters
    if generation is not None:
        query = query.where(Person.generation_id == generation)
    
    if branch_id:
        try:
            branch_uuid = UUID(branch_id)
            query = query.where(Person.branch_id == branch_uuid)
        except ValueError:
            pass
    
    if gender:
        query = query.where(Person.gender == gender)
    
    if visibility:
        query = query.where(Person.visibility == visibility)
    
    if search:
        search_pattern = f"%{search}%"
        query = query.where(
            Person.name.ilike(search_pattern) |
            Person.courtesy_name.ilike(search_pattern) |
            Person.art_name.ilike(search_pattern) |
            Person.alias.ilike(search_pattern)
        )
    
    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar()
    
    # Order and paginate
    query = query.order_by(Person.generation_id, Person.sort_order, Person.id)
    query = query.offset((page - 1) * page_size).limit(page_size)
    
    result = await db.execute(query)
    persons = result.scalars().all()
    
    return PersonListResponse(
        data=[await person_to_response(p, db) for p in persons],
        meta={
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
        }
    )


@router.get("/generations", response_model=dict)
async def list_generations(
    request: Request,
    db: AsyncSession = Depends(get_tenant_db),
):
    """List all generations with person count"""
    require_tenant(request)
    
    stmt = select(Generation).order_by(Generation.number)
    result = await db.execute(stmt)
    generations = result.scalars().all()
    
    data = []
    for gen in generations:
        # Count persons in this generation
        count_stmt = select(func.count()).where(Person.generation_id == gen.id)
        count = (await db.execute(count_stmt)).scalar()
        
        data.append({
            "id": gen.id,
            "number": gen.number,
            "is_spouse": gen.is_spouse,
            "name": gen.name,
            "description": gen.description,
            "person_count": count,
        })
    
    return {"success": True, "data": data}


@router.get("/branches", response_model=dict)
async def list_branches(
    request: Request,
    db: AsyncSession = Depends(get_tenant_db),
):
    """List all branches with person count"""
    require_tenant(request)
    
    stmt = select(Branch).order_by(Branch.name)
    result = await db.execute(stmt)
    branches = result.scalars().all()
    
    data = []
    for branch in branches:
        count_stmt = select(func.count()).where(Person.branch_id == branch.id)
        count = (await db.execute(count_stmt)).scalar()
        
        data.append({
            "id": str(branch.id),
            "name": branch.name,
            "description": branch.description,
            "location": branch.location,
            "person_count": count,
        })
    
    return {"success": True, "data": data}


@router.get("/{person_id}", response_model=dict)
async def get_person(
    person_id: str,
    request: Request,
    db: AsyncSession = Depends(get_tenant_db),
):
    """Get a single person by ID"""
    require_tenant(request)
    
    try:
        uuid = UUID(person_id)
    except ValueError:
        raise HTTPException(400, "Invalid person ID format")
    
    stmt = select(Person).where(Person.id == uuid)
    result = await db.execute(stmt)
    person = result.scalar_one_or_none()
    
    if not person:
        raise HTTPException(404, "Person not found")
    
    return {
        "success": True,
        "data": await person_to_response(person, db, include_relations=True),
    }


@router.post("", response_model=dict, status_code=201)
async def create_person(
    data: PersonCreate,
    request: Request,
    db: AsyncSession = Depends(get_tenant_db),
):
    """Create a new person"""
    require_tenant(request)
    
    # Check person quota
    quota_result = await quota_service.check_persons_quota(request.state.tenant.plan, db, Person)
    if not quota_result.allowed:
        raise HTTPException(403, format_quota_error(quota_result))
    
    # Validate father exists and is male
    if data.father_id:
        stmt = select(Person).where(Person.id == data.father_id)
        result = await db.execute(stmt)
        father = result.scalar_one_or_none()
        if not father:
            raise HTTPException(400, "Father not found")
        if father.gender != "M":
            raise HTTPException(400, "Father must be male")
    
    # Validate mother exists and is female
    if data.mother_id:
        stmt = select(Person).where(Person.id == data.mother_id)
        result = await db.execute(stmt)
        mother = result.scalar_one_or_none()
        if not mother:
            raise HTTPException(400, "Mother not found")
        if mother.gender != "F":
            raise HTTPException(400, "Mother must be female")
    
    # Validate generation exists
    if data.generation_id:
        stmt = select(Generation).where(Generation.id == data.generation_id)
        result = await db.execute(stmt)
        if not result.scalar_one_or_none():
            raise HTTPException(400, "Generation not found")
    
    # Validate branch exists
    if data.branch_id:
        stmt = select(Branch).where(Branch.id == data.branch_id)
        result = await db.execute(stmt)
        if not result.scalar_one_or_none():
            raise HTTPException(400, "Branch not found")
    
    # Create person
    person = Person(
        name=data.name,
        courtesy_name=data.courtesy_name,
        art_name=data.art_name,
        alias=data.alias,
        generation_char=data.generation_char,
        gender=data.gender,
        is_outsider=data.is_outsider,
        generation_id=data.generation_id,
        branch_id=data.branch_id,
        father_id=data.father_id,
        mother_id=data.mother_id,
        birth_year=data.birth_year,
        death_year=data.death_year,
        birth_place=data.birth_place,
        lunar_birthday=data.lunar_birthday,
        burial_place=data.burial_place,
        burial_fengshui=data.burial_fengshui,
        burial_direction=data.burial_direction,
        biography=data.biography,
        achievements=data.achievements,
        descendants_location=data.descendants_location,
        notes=data.notes,
        visibility=data.visibility,
        sort_order=data.sort_order,
    )
    
    db.add(person)
    await db.commit()
    await db.refresh(person)
    
    return {
        "success": True,
        "data": await person_to_response(person, db),
        "message": "Person created successfully",
    }


@router.put("/{person_id}", response_model=dict)
async def update_person(
    person_id: str,
    data: PersonUpdate,
    request: Request,
    db: AsyncSession = Depends(get_tenant_db),
):
    """Update a person"""
    require_tenant(request)
    
    try:
        uuid = UUID(person_id)
    except ValueError:
        raise HTTPException(400, "Invalid person ID format")
    
    stmt = select(Person).where(Person.id == uuid)
    result = await db.execute(stmt)
    person = result.scalar_one_or_none()
    
    if not person:
        raise HTTPException(404, "Person not found")
    
    # Update fields
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(person, field, value)
    
    person.updated_at = datetime.now(timezone.utc)
    
    await db.commit()
    await db.refresh(person)
    
    return {
        "success": True,
        "data": await person_to_response(person, db),
        "message": "Person updated successfully",
    }


@router.delete("/{person_id}", response_model=dict)
async def delete_person(
    person_id: str,
    request: Request,
    db: AsyncSession = Depends(get_tenant_db),
):
    """Delete a person"""
    require_tenant(request)
    
    try:
        uuid = UUID(person_id)
    except ValueError:
        raise HTTPException(400, "Invalid person ID format")
    
    stmt = select(Person).where(Person.id == uuid)
    result = await db.execute(stmt)
    person = result.scalar_one_or_none()
    
    if not person:
        raise HTTPException(404, "Person not found")
    
    # Check if person has children
    children_stmt = select(func.count()).where(Person.father_id == uuid)
    children_count = (await db.execute(children_stmt)).scalar()
    
    if children_count > 0:
        raise HTTPException(
            400,
            f"Cannot delete: person has {children_count} children. Remove or reassign children first."
        )
    
    # Delete spouse relations
    spouse_stmt = select(SpouseRelation).where(
        (SpouseRelation.husband_id == uuid) | (SpouseRelation.wife_id == uuid)
    )
    spouse_result = await db.execute(spouse_stmt)
    spouse_relations = spouse_result.scalars().all()
    
    for rel in spouse_relations:
        await db.delete(rel)
    
    # Delete person
    await db.delete(person)
    await db.commit()
    
    return {
        "success": True,
        "message": "Person deleted successfully",
    }


# ============ Spouse Relations ============

@router.get("/{person_id}/spouses", response_model=dict)
async def get_person_spouses(
    person_id: str,
    request: Request,
    db: AsyncSession = Depends(get_tenant_db),
):
    """Get spouses of a person"""
    require_tenant(request)
    
    try:
        uuid = UUID(person_id)
    except ValueError:
        raise HTTPException(400, "Invalid person ID format")
    
    # Get person
    stmt = select(Person).where(Person.id == uuid)
    result = await db.execute(stmt)
    person = result.scalar_one_or_none()
    
    if not person:
        raise HTTPException(404, "Person not found")
    
    # Get spouse relations
    if person.gender == "M":
        stmt = select(SpouseRelation).where(SpouseRelation.husband_id == uuid).order_by(SpouseRelation.sort_order)
    else:
        stmt = select(SpouseRelation).where(SpouseRelation.wife_id == uuid).order_by(SpouseRelation.sort_order)
    
    result = await db.execute(stmt)
    relations = result.scalars().all()
    
    data = []
    for rel in relations:
        # Get spouse info
        spouse_id = rel.wife_id if person.gender == "M" else rel.husband_id
        spouse_stmt = select(Person).where(Person.id == spouse_id)
        spouse_result = await db.execute(spouse_stmt)
        spouse = spouse_result.scalar_one_or_none()
        
        data.append({
            "id": str(rel.id),
            "spouse_id": str(spouse_id),
            "spouse_name": spouse.name if spouse else None,
            "relation_type": rel.relation_type,
            "source_info": rel.source_info,
            "sort_order": rel.sort_order,
        })
    
    return {"success": True, "data": data}


@router.post("/{person_id}/spouses", response_model=dict, status_code=201)
async def add_spouse(
    person_id: str,
    data: SpouseRelationCreate,
    request: Request,
    db: AsyncSession = Depends(get_tenant_db),
):
    """Add a spouse relation"""
    require_tenant(request)
    
    try:
        uuid = UUID(person_id)
    except ValueError:
        raise HTTPException(400, "Invalid person ID format")
    
    # Validate both persons exist
    stmt = select(Person).where(Person.id == data.husband_id)
    result = await db.execute(stmt)
    husband = result.scalar_one_or_none()
    
    stmt = select(Person).where(Person.id == data.wife_id)
    result = await db.execute(stmt)
    wife = result.scalar_one_or_none()
    
    if not husband or not wife:
        raise HTTPException(400, "Husband or wife not found")
    
    if husband.gender != "M":
        raise HTTPException(400, "Husband must be male")
    
    if wife.gender != "F":
        raise HTTPException(400, "Wife must be female")
    
    # Check if relation already exists
    stmt = select(SpouseRelation).where(
        SpouseRelation.husband_id == data.husband_id,
        SpouseRelation.wife_id == data.wife_id,
    )
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise HTTPException(400, "Spouse relation already exists")
    
    # Create relation
    relation = SpouseRelation(
        husband_id=data.husband_id,
        wife_id=data.wife_id,
        relation_type=data.relation_type,
        source_info=data.source_info,
        sort_order=data.sort_order,
    )
    
    db.add(relation)
    await db.commit()
    
    return {
        "success": True,
        "data": {
            "id": str(relation.id),
            "husband_id": str(relation.husband_id),
            "wife_id": str(relation.wife_id),
            "relation_type": relation.relation_type,
        },
        "message": "Spouse relation added successfully",
    }


@router.delete("/{person_id}/spouses/{spouse_id}", response_model=dict)
async def remove_spouse(
    person_id: str,
    spouse_id: str,
    request: Request,
    db: AsyncSession = Depends(get_tenant_db),
):
    """Remove a spouse relation"""
    require_tenant(request)
    
    try:
        person_uuid = UUID(person_id)
        spouse_uuid = UUID(spouse_id)
    except ValueError:
        raise HTTPException(400, "Invalid ID format")
    
    # Find and delete relation
    stmt = select(SpouseRelation).where(
        ((SpouseRelation.husband_id == person_uuid) & (SpouseRelation.wife_id == spouse_uuid)) |
        ((SpouseRelation.wife_id == person_uuid) & (SpouseRelation.husband_id == spouse_uuid))
    )
    result = await db.execute(stmt)
    relation = result.scalar_one_or_none()
    
    if not relation:
        raise HTTPException(404, "Spouse relation not found")
    
    await db.delete(relation)
    await db.commit()
    
    return {
        "success": True,
        "message": "Spouse relation removed successfully",
    }


# ============ 5-Generation Tree ============

@router.get("/{person_id}/tree", response_model=dict)
async def get_person_tree(
    person_id: str,
    request: Request,
    db: AsyncSession = Depends(get_tenant_db),
):
    """Get 5-generation tree (2 ancestors up, 2 descendants down) centered on person"""
    require_tenant(request)

    try:
        uuid = UUID(person_id)
    except ValueError:
        raise HTTPException(400, "Invalid person ID format")

    # Get center person
    stmt = select(Person).where(Person.id == uuid)
    result = await db.execute(stmt)
    center_person = result.scalar_one_or_none()

    if not center_person:
        raise HTTPException(404, "Person not found")

    # Build tree
    tree_data = await build_five_gen_tree(db, center_person)

    return {
        "success": True,
        "data": tree_data,
    }


async def build_five_gen_tree(db: AsyncSession, center_person: Person) -> dict:
    """Build 5-generation tree: 2 ancestors up, center, 2 descendants down"""

    async def get_person_with_spouse(person_id: UUID) -> dict:
        """Get person info with spouse"""
        stmt = select(Person).where(Person.id == person_id)
        result = await db.execute(stmt)
        person = result.scalar_one_or_none()
        if not person:
            return None

        # Get spouse (first one if multiple)
        spouse_stmt = select(SpouseRelation).where(
            (SpouseRelation.husband_id == person_id) | (SpouseRelation.wife_id == person_id)
        ).limit(1)
        spouse_result = await db.execute(spouse_stmt)
        spouse_rel = spouse_result.scalar_one_or_none()

        spouse_info = None
        if spouse_rel:
            spouse_id = spouse_rel.wife_id if person.gender == "M" else spouse_rel.husband_id
            spouse_stmt2 = select(Person).where(Person.id == spouse_id)
            spouse_result2 = await db.execute(spouse_stmt2)
            spouse = spouse_result2.scalar_one_or_none()
            if spouse:
                spouse_info = {
                    "id": str(spouse.id),
                    "name": spouse.name,
                    "gender": spouse.gender,
                }

        return {
            "id": str(person.id),
            "name": person.name,
            "gender": person.gender,
            "birth_year": person.birth_year,
            "death_year": person.death_year,
            "generation_id": person.generation_id,
            "spouse": spouse_info,
        }

    async def get_ancestors(person: Person, levels: int) -> list:
        """Get ancestors up N levels"""
        ancestors = []
        current = person

        for _ in range(levels):
            if not current.father_id:
                break

            # Get father
            father_info = await get_person_with_spouse(current.father_id)
            if father_info:
                ancestors.append(father_info)
                # Move up to father
                stmt = select(Person).where(Person.id == current.father_id)
                result = await db.execute(stmt)
                current = result.scalar_one_or_none()
                if not current:
                    break
            else:
                break

        return ancestors

    async def get_descendants(person_id: UUID, levels: int) -> list:
        """Get descendants down N levels recursively"""
        if levels <= 0:
            return []

        # Get children
        stmt = select(Person).where(Person.father_id == person_id).order_by(Person.sort_order, Person.birth_year)
        result = await db.execute(stmt)
        children = result.scalars().all()

        descendants = []
        for child in children:
            child_info = await get_person_with_spouse(child.id)
            if child_info:
                # Recursively get grandchildren
                child_info["children"] = await get_descendants(child.id, levels - 1)
                descendants.append(child_info)

        return descendants

    # Build tree structure
    center_info = await get_person_with_spouse(center_person.id)

    # Get 2 levels of ancestors (reverse order: oldest first)
    ancestors = await get_ancestors(center_person, 2)
    ancestors.reverse()

    # Get 2 levels of descendants
    descendants = await get_descendants(center_person.id, 2)

    return {
        "center": center_info,
        "ancestors": ancestors,  # [grandfather, father]
        "descendants": descendants,  # [children with grandchildren]
        "total_generations": len(ancestors) + 1 + (1 if descendants else 0),
    }


# ============ Helper Functions ============

async def person_to_response(
    person: Person,
    db: AsyncSession,
    include_relations: bool = False
) -> PersonResponse:
    """Convert Person model to response schema"""
    
    response = PersonResponse(
        id=str(person.id),
        name=person.name,
        courtesy_name=person.courtesy_name,
        art_name=person.art_name,
        alias=person.alias,
        generation_char=person.generation_char,
        gender=person.gender,
        is_outsider=person.is_outsider,
        generation_id=person.generation_id,
        branch_id=str(person.branch_id) if person.branch_id else None,
        father_id=str(person.father_id) if person.father_id else None,
        mother_id=str(person.mother_id) if person.mother_id else None,
        birth_year=person.birth_year,
        death_year=person.death_year,
        birth_place=person.birth_place,
        lunar_birthday=person.lunar_birthday,
        burial_place=person.burial_place,
        burial_fengshui=person.burial_fengshui,
        burial_direction=person.burial_direction,
        biography=person.biography,
        achievements=person.achievements,
        descendants_location=person.descendants_location,
        notes=person.notes,
        visibility=person.visibility,
        sort_order=person.sort_order,
        avatar=person.avatar,
        created_at=person.created_at,
        updated_at=person.updated_at,
        full_name=person.full_name if hasattr(person, 'full_name') else None,
    )
    
    # Fetch related names
    if person.generation_id:
        stmt = select(Generation).where(Generation.id == person.generation_id)
        result = await db.execute(stmt)
        gen = result.scalar_one_or_none()
        response.generation_name = gen.name if gen else f"第{person.generation_id}世"
    
    if person.branch_id:
        stmt = select(Branch).where(Branch.id == person.branch_id)
        result = await db.execute(stmt)
        branch = result.scalar_one_or_none()
        response.branch_name = branch.name if branch else None
    
    if person.father_id:
        stmt = select(Person).where(Person.id == person.father_id)
        result = await db.execute(stmt)
        father = result.scalar_one_or_none()
        response.father_name = father.name if father else None
    
    if person.mother_id:
        stmt = select(Person).where(Person.id == person.mother_id)
        result = await db.execute(stmt)
        mother = result.scalar_one_or_none()
        response.mother_name = mother.name if mother else None
    
    return response


# ============ Batch Import ============

from fastapi import UploadFile, File
import csv
import io

@router.post("/batch-import", response_model=dict)
async def batch_import_persons(
    request: Request,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_tenant_db),
):
    """
    Batch import persons from CSV file.
    Required columns: name, gender
    Optional: generation_id, courtesy_name, art_name, birth_year, death_year, birth_place, biography, visibility
    """
    tenant = require_tenant(request)
    
    # Check quota
    quota_result = await quota_service.check_persons_quota(tenant.plan, db, Person)
    if not quota_result.allowed:
        raise HTTPException(403, format_quota_error(quota_result))
    
    # Read file
    content = await file.read()
    
    # Try different encodings
    text = None
    for encoding in ["utf-8-sig", "utf-8", "gbk", "gb18030"]:
        try:
            text = content.decode(encoding)
            break
        except UnicodeDecodeError:
            continue
    
    if text is None:
        raise HTTPException(400, "无法识别文件编码，请使用 UTF-8 或 GBK 编码")
    
    # Parse CSV
    reader = csv.DictReader(io.StringIO(text))
    
    success_count = 0
    failed_count = 0
    errors = []
    
    for row_num, row in enumerate(reader, start=2):
        try:
            name = row.get("name", "").strip()
            gender = row.get("gender", "M").strip().upper()
            
            if not name:
                errors.append(f"第{row_num}行: 姓名不能为空")
                failed_count += 1
                continue
            
            if gender not in ["M", "F"]:
                gender = "M"
            
            person_data = {
                "name": name,
                "gender": gender,
                "courtesy_name": row.get("courtesy_name", "").strip() or None,
                "art_name": row.get("art_name", "").strip() or None,
                "birth_year": int(row.get("birth_year", 0)) if row.get("birth_year", "").strip() else None,
                "death_year": int(row.get("death_year", 0)) if row.get("death_year", "").strip() else None,
                "birth_place": row.get("birth_place", "").strip() or None,
                "biography": row.get("biography", "").strip() or None,
                "visibility": row.get("visibility", "public").strip() or "public",
            }
            
            gen_str = row.get("generation_id", "").strip()
            if gen_str:
                try:
                    person_data["generation_id"] = int(gen_str)
                except ValueError:
                    pass
            
            person = Person(**person_data)
            db.add(person)
            success_count += 1
            
        except Exception as e:
            errors.append(f"第{row_num}行: {str(e)}")
            failed_count += 1
    
    await db.commit()
    
    return {
        "success": True,
        "data": {
            "success": success_count,
            "failed": failed_count,
            "errors": errors[:20],
        },
        "message": f"成功导入 {success_count} 条，失败 {failed_count} 条",
    }
