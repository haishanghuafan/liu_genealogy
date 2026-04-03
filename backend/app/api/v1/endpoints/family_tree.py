"""
Family Tree API endpoints
"""
from typing import Any, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_tenant_db
from app.middleware.tenant import require_tenant
from app.models.system import Tenant
from app.models.tenant import Person

router = APIRouter(prefix="/family-tree", tags=["Family Tree"])


# Schemas
class TreeNode(BaseModel):
    id: str
    name: str
    generation: Optional[int] = None
    gender: str = "M"
    birthYear: Optional[int] = None
    deathYear: Optional[int] = None
    avatar: Optional[str] = None
    courtesyName: Optional[str] = None
    children: list["TreeNode"] = []
    
    class Config:
        from_attributes = True


class TreeStats(BaseModel):
    total_persons: int
    generations: list[dict]
    max_generation: int


# Endpoints
@router.get("", response_model=dict)
async def get_family_tree(
    request: Request,
    root_id: Optional[str] = Query(None, description="Root person ID"),
    depth: int = Query(4, ge=1, le=10, description="Tree depth"),
    db: AsyncSession = Depends(get_tenant_db),
):
    """Get family tree structure for visualization"""
    tenant = require_tenant(request)
    
    if root_id:
        # Build tree from specific root
        try:
            root_uuid = UUID(root_id)
        except ValueError:
            raise HTTPException(400, "Invalid person ID format")
        
        tree = await build_tree_from_root(db, root_uuid, depth)
    else:
        # Find the first person (usually the ancestor) as root
        tree = await build_full_tree(db, depth)
    
    return {
        "success": True,
        "data": tree,
    }


async def build_tree_from_root(
    db: AsyncSession,
    root_id: UUID,
    max_depth: int
) -> Optional[TreeNode]:
    """Build tree from a specific root person"""
    
    # Get root person
    stmt = select(Person).where(Person.id == root_id)
    result = await db.execute(stmt)
    root = result.scalar_one_or_none()
    
    if not root:
        return None
    
    # Build tree recursively
    return await build_node_tree(db, root, max_depth)


async def build_full_tree(db: AsyncSession, max_depth: int) -> Optional[TreeNode]:
    """Build full tree starting from earliest ancestor"""
    
    # Find person without father (earliest ancestor)
    stmt = (
        select(Person)
        .where(Person.father_id == None)
        .order_by(Person.generation_id)
        .limit(1)
    )
    result = await db.execute(stmt)
    root = result.scalar_one_or_none()
    
    if not root:
        # Fallback: get first person by generation
        stmt = select(Person).order_by(Person.generation_id).limit(1)
        result = await db.execute(stmt)
        root = result.scalar_one_or_none()
    
    if not root:
        return None
    
    return await build_node_tree(db, root, max_depth)


async def build_node_tree(
    db: AsyncSession,
    person: Person,
    remaining_depth: int
) -> TreeNode:
    """Recursively build tree node with children"""
    
    node = TreeNode(
        id=str(person.id),
        name=person.name,
        generation=person.generation_id,
        gender=person.gender,
        birthYear=person.birth_year,
        deathYear=person.death_year,
        avatar=person.avatar,
        courtesyName=person.courtesy_name,
        children=[],
    )
    
    # Recursively get children if depth allows
    if remaining_depth > 0:
        # Get children (where this person is father)
        stmt = (
            select(Person)
            .where(Person.father_id == person.id)
            .order_by(Person.sort_order, Person.id)
        )
        result = await db.execute(stmt)
        children = result.scalars().all()
        
        for child in children:
            child_node = await build_node_tree(db, child, remaining_depth - 1)
            node.children.append(child_node)
    
    return node


@router.get("/ancestors/{person_id}", response_model=dict)
async def get_ancestors(
    person_id: str,
    request: Request,
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_tenant_db),
):
    """Get ancestor chain of a person"""
    tenant = require_tenant(request)
    
    try:
        uuid = UUID(person_id)
    except ValueError:
        raise HTTPException(400, "Invalid person ID format")
    
    ancestors = []
    current_id = uuid
    visited = set()
    
    for _ in range(limit):
        if current_id in visited:
            break
        visited.add(current_id)
        
        stmt = select(Person).where(Person.id == current_id)
        result = await db.execute(stmt)
        person = result.scalar_one_or_none()
        
        if not person:
            break
        
        ancestors.append({
            "id": str(person.id),
            "name": person.name,
            "generation": person.generation_id,
            "gender": person.gender,
        })
        
        # Move to father
        if person.father_id:
            current_id = person.father_id
        else:
            break
    
    return {
        "success": True,
        "data": ancestors,
    }


@router.get("/descendants/{person_id}", response_model=dict)
async def get_descendants(
    person_id: str,
    request: Request,
    depth: int = Query(5, ge=1, le=10),
    db: AsyncSession = Depends(get_tenant_db),
):
    """Get descendants of a person"""
    tenant = require_tenant(request)
    
    try:
        uuid = UUID(person_id)
    except ValueError:
        raise HTTPException(400, "Invalid person ID format")
    
    # Get root person
    stmt = select(Person).where(Person.id == uuid)
    result = await db.execute(stmt)
    root = result.scalar_one_or_none()
    
    if not root:
        raise HTTPException(404, "Person not found")
    
    # Build descendants tree
    tree = await build_node_tree(db, root, depth)
    
    return {
        "success": True,
        "data": tree,
    }


@router.get("/statistics", response_model=dict)
async def get_tree_statistics(
    request: Request,
    db: AsyncSession = Depends(get_tenant_db),
):
    """Get family tree statistics"""
    tenant = require_tenant(request)
    
    # Total persons
    stmt = select(Person)
    result = await db.execute(stmt)
    all_persons = result.scalars().all()
    
    total = len(all_persons)
    
    # By generation
    gen_counts: dict[int, int] = {}
    for p in all_persons:
        if p.generation_id:
            gen_counts[p.generation_id] = gen_counts.get(p.generation_id, 0) + 1
    
    generations = [
        {"generation": gen, "count": count}
        for gen, count in sorted(gen_counts.items())
    ]
    
    max_gen = max(gen_counts.keys()) if gen_counts else 0
    
    return {
        "success": True,
        "data": {
            "total_persons": total,
            "generations": generations,
            "max_generation": max_gen,
        },
    }


# Update forward references for recursive model
TreeNode.model_rebuild()
