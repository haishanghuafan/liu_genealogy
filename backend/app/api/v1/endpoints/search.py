"""
Advanced search endpoints - full-text search with filters
"""
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel
from sqlalchemy import func, select, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_tenant_db
from app.core.services import meilisearch_service
from app.middleware.tenant import require_tenant
from app.models.tenant import Person, Generation, Branch, SpouseRelation

router = APIRouter(prefix="/search", tags=["Search"])


# ============ Schemas ============

class SearchResult(BaseModel):
    id: str
    type: str  # person, branch, generation
    title: str
    subtitle: Optional[str]
    highlights: list[str]
    score: float = 0.0


class SearchResponse(BaseModel):
    success: bool = True
    data: list[SearchResult]
    meta: dict


class AdvancedSearchParams:
    """Advanced search parameters"""
    q: str = Query("", max_length=200, description="Search query")
    page: int = Query(1, ge=1)
    page_size: int = Query(20, ge=1, le=100)
    
    # Filters
    gender: Optional[str] = Query(None, pattern="^(M|F)$")
    generation_id: Optional[int] = Query(None)
    branch_id: Optional[str] = Query(None)
    birth_year_from: Optional[int] = Query(None)
    birth_year_to: Optional[int] = Query(None)
    has_biography: Optional[bool] = Query(None)
    visibility: Optional[str] = Query(None, pattern="^(public|member|private)$")
    sort_by: Optional[str] = Query("relevance", pattern="^(relevance|name|birth_year|generation|created_at)$")
    sort_order: Optional[str] = Query("desc", pattern="^(asc|desc)$")


# ============ Endpoints ============

@router.get("", response_model=SearchResponse)
async def search(
    request: Request,
    params: AdvancedSearchParams = Depends(),
    db: AsyncSession = Depends(get_tenant_db),
):
    """
    Search persons with advanced filters.
    Uses Meilisearch if available, falls back to SQL LIKE.
    """
    tenant = require_tenant(request)
    
    results: list[SearchResult] = []
    total = 0
    
    # Try Meilisearch first
    if meilisearch_service.is_available and params.q:
        try:
            results, total = await _search_meilisearch(
                tenant_id=str(tenant.id),
                query=params.q,
                page=params.page,
                page_size=params.page_size,
                filters=_build_meili_filters(params),
            )
            return SearchResponse(
                data=results,
                meta={
                    "total": total,
                    "page": params.page,
                    "page_size": params.page_size,
                    "source": "meilisearch",
                },
            )
        except Exception:
            pass  # Fall back to SQL
    
    # SQL fallback
    results, total = await _search_sql(
        db=db,
        query=params.q,
        page=params.page,
        page_size=params.page_size,
        gender=params.gender,
        generation_id=params.generation_id,
        branch_id=params.branch_id,
        birth_year_from=params.birth_year_from,
        birth_year_to=params.birth_year_to,
        has_biography=params.has_biography,
        visibility=params.visibility,
        sort_by=params.sort_by,
        sort_order=params.sort_order,
    )
    
    return SearchResponse(
        data=results,
        meta={
            "total": total,
            "page": params.page,
            "page_size": params.page_size,
            "source": "sql",
        },
    )


@router.get("/advanced", response_model=SearchResponse)
async def advanced_search(
    request: Request,
    params: AdvancedSearchParams = Depends(),
    db: AsyncSession = Depends(get_tenant_db),
):
    """
    Advanced search with all filters applied.
    Always uses SQL for precise filtering.
    """
    tenant = require_tenant(request)
    
    results, total = await _search_sql(
        db=db,
        query=params.q,
        page=params.page,
        page_size=params.page_size,
        gender=params.gender,
        generation_id=params.generation_id,
        branch_id=params.branch_id,
        birth_year_from=params.birth_year_from,
        birth_year_to=params.birth_year_to,
        has_biography=params.has_biography,
        visibility=params.visibility,
        sort_by=params.sort_by,
        sort_order=params.sort_order,
    )
    
    return SearchResponse(
        data=results,
        meta={
            "total": total,
            "page": params.page,
            "page_size": params.page_size,
            "source": "sql",
        },
    )


@router.get("/suggestions", response_model=dict)
async def search_suggestions(
    request: Request,
    q: str = Query("", min_length=1, max_length=50),
    limit: int = Query(5, ge=1, le=10),
    db: AsyncSession = Depends(get_tenant_db),
):
    """Get search suggestions for autocomplete"""
    tenant = require_tenant(request)
    
    if not q:
        return {"success": True, "data": []}
    
    search_pattern = f"%{q}%"
    
    stmt = select(Person).where(
        or_(
            Person.name.ilike(search_pattern),
            Person.courtesy_name.ilike(search_pattern),
            Person.art_name.ilike(search_pattern),
            Person.alias.ilike(search_pattern),
        )
    ).limit(limit)
    
    result = await db.execute(stmt)
    persons = result.scalars().all()
    
    suggestions = []
    for p in persons:
        text = p.name
        if p.courtesy_name:
            text += f"（字{p.courtesy_name}）"
        suggestions.append({
            "id": str(p.id),
            "text": text,
            "type": "person",
        })
    
    return {"success": True, "data": suggestions}


# ============ Helper Functions ============

def _build_meili_filters(params: AdvancedSearchParams) -> str:
    """Build Meilisearch filter string"""
    filters = []
    
    if params.gender:
        filters.append(f"gender = {params.gender}")
    if params.generation_id:
        filters.append(f"generation_id = {params.generation_id}")
    if params.branch_id:
        filters.append(f"branch_id = {params.branch_id}")
    if params.visibility:
        filters.append(f'visibility = "{params.visibility}"')
    if params.birth_year_from:
        filters.append(f"birth_year >= {params.birth_year_from}")
    if params.birth_year_to:
        filters.append(f"birth_year <= {params.birth_year_to}")
    if params.has_biography:
        filters.append("biography IS NOT NULL AND biography != ''")
    
    return " AND ".join(filters)


async def _search_meilisearch(
    tenant_id: str,
    query: str,
    page: int,
    page_size: int,
    filters: str,
) -> tuple[list[SearchResult], int]:
    """Search using Meilisearch"""
    index = meilisearch_service.client.index(f"persons_{tenant_id}")
    
    offset = (page - 1) * page_size
    results = index.search(
        query,
        limit=page_size,
        offset=offset,
        filter_expr=filters if filters else None,
        attributes_to_highlight=["name", "courtesy_name", "biography"],
    )
    
    total = results.estimated_total_hits or 0
    hits = results.hits
    
    search_results = []
    for hit in hits:
        formatted = hit.get("_formatted", {})
        highlights = []
        
        for key, value in formatted.items():
            if isinstance(value, str) and "<mark>" in value:
                highlights.append(value.replace("<mark>", "").replace("</mark>", ""))
        
        search_results.append(SearchResult(
            id=hit["id"],
            type="person",
            title=formatted.get("name", hit.get("name", "")),
            subtitle=f"第{hit.get('generation_id', '?')}世",
            highlights=highlights[:3],
            score=hit.get("_rankingScore", 0),
        ))
    
    return search_results, total


async def _search_sql(
    db: AsyncSession,
    query: str,
    page: int,
    page_size: int,
    gender: Optional[str] = None,
    generation_id: Optional[int] = None,
    branch_id: Optional[str] = None,
    birth_year_from: Optional[int] = None,
    birth_year_to: Optional[int] = None,
    has_biography: Optional[bool] = None,
    visibility: Optional[str] = None,
    sort_by: str = "relevance",
    sort_order: str = "desc",
) -> tuple[list[SearchResult], int]:
    """Search using SQL"""
    stmt = select(Person)
    
    # Text search
    if query:
        search_pattern = f"%{query}%"
        stmt = stmt.where(
            or_(
                Person.name.ilike(search_pattern),
                Person.courtesy_name.ilike(search_pattern),
                Person.art_name.ilike(search_pattern),
                Person.alias.ilike(search_pattern),
                Person.biography.ilike(search_pattern),
                Person.achievements.ilike(search_pattern),
                Person.birth_place.ilike(search_pattern),
                Person.burial_place.ilike(search_pattern),
            )
        )
    
    # Apply filters
    if gender:
        stmt = stmt.where(Person.gender == gender)
    if generation_id:
        stmt = stmt.where(Person.generation_id == generation_id)
    if branch_id:
        try:
            stmt = stmt.where(Person.branch_id == UUID(branch_id))
        except ValueError:
            pass
    if birth_year_from:
        stmt = stmt.where(Person.birth_year >= birth_year_from)
    if birth_year_to:
        stmt = stmt.where(Person.birth_year <= birth_year_to)
    if has_biography:
        stmt = stmt.where(Person.biography.isnot(None))
        stmt = stmt.where(Person.biography != "")
    if visibility:
        stmt = stmt.where(Person.visibility == visibility)
    
    # Count
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = (await db.execute(count_stmt)).scalar()
    
    # Sorting
    if sort_by == "name":
        order_col = Person.name
    elif sort_by == "birth_year":
        order_col = Person.birth_year
    elif sort_by == "generation":
        order_col = Person.generation_id
    elif sort_by == "created_at":
        order_col = Person.created_at
    else:
        order_col = Person.generation_id
    
    if sort_order == "asc":
        stmt = stmt.order_by(order_col.asc().nullslast(), Person.sort_order.asc())
    else:
        stmt = stmt.order_by(order_col.desc().nullsfirst(), Person.sort_order.asc())
    
    # Paginate
    stmt = stmt.offset((page - 1) * page_size).limit(page_size)
    
    result = await db.execute(stmt)
    persons = result.scalars().all()
    
    search_results = []
    for p in persons:
        # Generate highlights from matching text
        highlights = []
        subtitle_parts = []
        
        if p.generation_id:
            subtitle_parts.append(f"第{p.generation_id}世")
        if p.birth_year:
            subtitle_parts.append(f"{p.birth_year}年")
        if p.gender == "M":
            subtitle_parts.append("男")
        else:
            subtitle_parts.append("女")
        
        title = p.name
        if p.courtesy_name:
            title += f"（字{p.courtesy_name}）"
        
        if p.biography:
            highlights.append(p.biography[:100] + "...")
        if p.birth_place:
            highlights.append(f"出生地: {p.birth_place}")
        if p.achievements:
            highlights.append(p.achievements[:100] + "...")
        
        search_results.append(SearchResult(
            id=str(p.id),
            type="person",
            title=title,
            subtitle=" · ".join(subtitle_parts) if subtitle_parts else None,
            highlights=highlights[:3],
            score=0.0,  # SQL search has no relevance score
        ))
    
    return search_results, total