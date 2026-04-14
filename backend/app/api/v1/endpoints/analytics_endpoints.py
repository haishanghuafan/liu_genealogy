"""
Analytics API endpoints for tracking and statistics
"""
from typing import Optional

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_tenant_db
from app.middleware.tenant import require_tenant
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.post("/track", response_model=dict)
async def track_page_view(
    request: Request,
    page_type: str,
    page_id: Optional[str] = None,
    db: AsyncSession = Depends(get_tenant_db),
):
    """Track a page view"""
    tenant = require_tenant(request)
    
    # Get client info
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent", "")
    
    # Try to get user info from auth
    user_id = None
    is_authenticated = False
    
    auth_header = request.headers.get("authorization")
    if auth_header and auth_header.startswith("Bearer "):
        # User is authenticated (simplified - in production verify token)
        is_authenticated = True
    
    # Track view
    service = AnalyticsService(db)
    
    from uuid import UUID
    page_uuid = UUID(page_id) if page_id else None
    
    await service.track_page_view(
        page_type=page_type,
        tenant_slug=tenant.slug,
        page_id=page_uuid,
        ip_address=ip_address,
        user_agent=user_agent,
        user_id=user_id,
        is_authenticated=is_authenticated,
    )
    
    return {"success": True, "message": "View tracked"}


@router.get("/summary", response_model=dict)
async def get_analytics_summary(
    request: Request,
    days: int = 30,
    db: AsyncSession = Depends(get_tenant_db),
):
    """Get summary statistics for the last N days"""
    tenant = require_tenant(request)
    
    service = AnalyticsService(db)
    stats = await service.get_summary_stats(tenant.slug, days)
    
    return {
        "success": True,
        "data": stats
    }


@router.get("/daily", response_model=dict)
async def get_daily_stats(
    request: Request,
    days: int = 30,
    db: AsyncSession = Depends(get_tenant_db),
):
    """Get daily statistics for the last N days"""
    tenant = require_tenant(request)
    
    service = AnalyticsService(db)
    daily_stats = await service.get_daily_stats(tenant.slug, days)
    
    return {
        "success": True,
        "data": [
            {
                "date": stat.date.isoformat(),
                "total_views": stat.total_views,
                "unique_visitors": stat.unique_visitors,
                "authenticated_views": stat.authenticated_views,
                "anonymous_views": stat.anonymous_views,
                "person_views": stat.person_views,
                "branch_views": stat.branch_views,
                "generation_views": stat.generation_views,
                "family_tree_views": stat.family_tree_views,
            }
            for stat in daily_stats
        ]
    }


@router.get("/popular", response_model=dict)
async def get_popular_pages(
    request: Request,
    page_type: Optional[str] = None,
    days: int = 7,
    limit: int = 10,
    db: AsyncSession = Depends(get_tenant_db),
):
    """Get most viewed pages"""
    tenant = require_tenant(request)
    
    service = AnalyticsService(db)
    popular = await service.get_popular_pages(
        tenant.slug,
        page_type=page_type,
        days=days,
        limit=limit,
    )
    
    return {
        "success": True,
        "data": popular
    }
