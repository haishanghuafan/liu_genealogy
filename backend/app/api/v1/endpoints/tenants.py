"""
Tenant management endpoints
"""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models import Tenant, User

router = APIRouter(prefix="/tenants", tags=["Tenants"])


# Schemas
class TenantCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    slug: str = Field(..., min_length=2, max_length=50, pattern="^[a-z0-9-]+$")
    surname: str = Field(..., min_length=1, max_length=50)
    is_public: bool = True


class TenantResponse(BaseModel):
    id: str
    name: str
    slug: str
    surname: str
    is_public: bool
    plan: str
    created_at: str
    
    class Config:
        from_attributes = True


class TenantListResponse(BaseModel):
    success: bool = True
    data: list[TenantResponse]
    meta: dict


# Endpoints
@router.get("", response_model=TenantListResponse)
async def list_tenants(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    surname: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """List all public tenants"""
    query = select(Tenant).where(Tenant.is_public == True, Tenant.is_active == True)
    
    if surname:
        query = query.where(Tenant.surname.ilike(f"%{surname}%"))
    
    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar()
    
    # Paginate
    query = query.offset((page - 1) * page_size).limit(page_size)
    query = query.order_by(Tenant.created_at.desc())
    
    result = await db.execute(query)
    tenants = result.scalars().all()
    
    return TenantListResponse(
        data=[
            TenantResponse(
                id=str(t.id),
                name=t.name,
                slug=t.slug,
                surname=t.surname,
                is_public=t.is_public,
                plan=t.plan,
                created_at=t.created_at.isoformat(),
            )
            for t in tenants
        ],
        meta={
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
        },
    )


@router.get("/{slug}", response_model=TenantResponse)
async def get_tenant(
    slug: str,
    db: AsyncSession = Depends(get_db),
):
    """Get tenant by slug"""
    stmt = select(Tenant).where(Tenant.slug == slug)
    result = await db.execute(stmt)
    tenant = result.scalar_one_or_none()
    
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found",
        )
    
    return TenantResponse(
        id=str(tenant.id),
        name=tenant.name,
        slug=tenant.slug,
        surname=tenant.surname,
        is_public=tenant.is_public,
        plan=tenant.plan,
        created_at=tenant.created_at.isoformat(),
    )


@router.post("", response_model=TenantResponse, status_code=status.HTTP_201_CREATED)
async def create_tenant(
    data: TenantCreate,
    db: AsyncSession = Depends(get_db),
    # user: User = Depends(require_superuser),  # TODO: Enable after auth
):
    """Create a new tenant (superuser only)"""
    # Check if slug already exists
    stmt = select(Tenant).where(Tenant.slug == data.slug)
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Slug already exists",
        )
    
    # Create schema name from slug
    schema_name = f"tenant_{data.slug.replace('-', '_')}"
    
    # Create tenant
    tenant = Tenant(
        name=data.name,
        slug=data.slug,
        surname=data.surname,
        is_public=data.is_public,
        schema_name=schema_name,
        neo4j_database=f"tenant_{data.slug}",
    )
    db.add(tenant)
    
    # TODO: Create PostgreSQL schema
    # TODO: Create Neo4j database
    # TODO: Run migrations on tenant schema
    
    await db.commit()
    await db.refresh(tenant)
    
    return TenantResponse(
        id=str(tenant.id),
        name=tenant.name,
        slug=tenant.slug,
        surname=tenant.surname,
        is_public=tenant.is_public,
        plan=tenant.plan,
        created_at=tenant.created_at.isoformat(),
    )
