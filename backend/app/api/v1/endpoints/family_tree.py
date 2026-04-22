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
from app.models.tenant import Person, SpouseRelation

router = APIRouter(prefix="/family-tree", tags=["Family Tree"])


# Schemas
class SpouseInfo(BaseModel):
    id: str
    name: str
    gender: str = "F"
    
    class Config:
        from_attributes = True


class TreeNode(BaseModel):
    id: str
    name: str
    generation: Optional[int] = None
    gender: str = "M"
    birthYear: Optional[int] = None
    deathYear: Optional[int] = None
    avatar: Optional[str] = None
    courtesyName: Optional[str] = None
    isSpouse: bool = False  # 标记是否为配偶节点
    children: list["TreeNode"] = []
    
    class Config:
        from_attributes = True


class ForestResponse(BaseModel):
    trees: list[TreeNode]
    total_persons: int
    total_trees: int


class TreeStats(BaseModel):
    total_persons: int
    generations: list[dict]
    max_generation: int


# Endpoints
@router.get("", response_model=dict)
async def get_family_tree(
    request: Request,
    root_id: Optional[str] = Query(None, description="Root person ID"),
    depth: int = Query(10, ge=1, le=15, description="Tree depth"),
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


async def build_full_tree(db: AsyncSession, max_depth: int) -> dict:
    """Build full tree as a forest (multiple root nodes)"""

    from sqlalchemy import func

    stmt_count = select(func.count(Person.id))
    result = await db.execute(stmt_count)
    total_persons = result.scalar()

    # 只找乾正作为主树根
    stmt = (
        select(Person)
        .where(Person.father_id == None, Person.gender == "M", Person.generation_id == 1)
        .order_by(Person.generation_id, Person.sort_order, Person.id)
    )
    result = await db.execute(stmt)
    all_roots = result.scalars().all()

    if not all_roots:
        return {"trees": [], "total_persons": total_persons, "total_trees": 0}

    trees = []

    for root in all_roots:
        child_stmt = select(func.count(Person.id)).where(Person.father_id == root.id)
        child_result = await db.execute(child_stmt)
        has_children = child_result.scalar() > 0

        # 有子女的男性作为树根，乾正作为始祖始终显示
        if has_children or root.name == "乾正":
            tree = await build_node_tree(db, root, max_depth)
            trees.append(tree)

    return {
        "trees": trees,
        "total_persons": total_persons,
        "total_trees": len(trees),
    }


async def build_node_tree(
    db: AsyncSession,
    person: Person,
    remaining_depth: int
) -> TreeNode:
    """Recursively build tree node with spouses as separate branches"""
    
    # 获取所有配偶信息
    if person.gender == "M":
        # 查找所有妻子
        stmt = (
            select(Person, SpouseRelation)
            .join(SpouseRelation, SpouseRelation.wife_id == Person.id)
            .where(SpouseRelation.husband_id == person.id)
            .order_by(SpouseRelation.sort_order)
        )
    else:
        # 查找所有丈夫
        stmt = (
            select(Person, SpouseRelation)
            .join(SpouseRelation, SpouseRelation.husband_id == Person.id)
            .where(SpouseRelation.wife_id == person.id)
            .order_by(SpouseRelation.sort_order)
        )
    
    result = await db.execute(stmt)
    spouse_relations = result.all()
    
    # 构建节点
    node = TreeNode(
        id=str(person.id),
        name=person.name,
        generation=person.generation_id,
        gender=person.gender,
        birthYear=person.birth_year,
        deathYear=person.death_year,
        avatar=person.avatar,
        courtesyName=person.courtesy_name,
        isSpouse=False,
        children=[],
    )
    
    # 为每个配偶创建独立的子节点
    if remaining_depth > 0:
        for spouse_person, spouse_rel in spouse_relations:
            # 创建配偶节点
            spouse_node = TreeNode(
                id=str(spouse_person.id),
                name=spouse_person.name,
                generation=spouse_person.generation_id,
                gender=spouse_person.gender,
                birthYear=spouse_person.birth_year,
                deathYear=spouse_person.death_year,
                avatar=spouse_person.avatar,
                courtesyName=spouse_person.courtesy_name,
                isSpouse=True,
                children=[],
            )
            
            # 获取该配偶的子女
            if person.gender == "M":
                # person是父亲，spouse是母亲
                stmt_children = (
                    select(Person)
                    .where(
                        Person.father_id == person.id,
                        Person.mother_id == spouse_person.id
                    )
                    .order_by(Person.sort_order, Person.id)
                )
            else:
                # person是母亲，spouse是父亲
                stmt_children = (
                    select(Person)
                    .where(
                        Person.mother_id == person.id,
                        Person.father_id == spouse_person.id
                    )
                    .order_by(Person.sort_order, Person.id)
                )
            
            result_children = await db.execute(stmt_children)
            children_persons = result_children.scalars().all()
            
            for child in children_persons:
                child_node = await build_node_tree(db, child, remaining_depth - 1)
                spouse_node.children.append(child_node)
            
            node.children.append(spouse_node)
    
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
