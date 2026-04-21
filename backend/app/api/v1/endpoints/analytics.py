"""
Analytics API endpoints
"""
from datetime import date, timedelta
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request
from pydantic import BaseModel
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_tenant_db
from app.middleware.tenant import require_tenant
from app.middleware.auth import get_current_user_required
from app.models.tenant import DailyVisitStats, PageView

router = APIRouter(prefix="/analytics", tags=["Analytics"])


# ============ Page Visit Tracking ============

class TrackVisitRequest(BaseModel):
    path: str
    page_type: Optional[str] = "page"


@router.post("/track", response_model=dict)
async def track_page_visit(
    request: Request,
    track_req: TrackVisitRequest,
    db: AsyncSession = Depends(get_tenant_db),
    user = Depends(get_current_user_required),
):
    """Track a page visit from frontend"""
    tenant = require_tenant(request)
    
    from app.services.analytics_service import AnalyticsService
    
    # Get client info from request
    ip_address = request.headers.get("X-Forwarded-For", "").split(",")[0].strip() if request.headers.get("X-Forwarded-For") else (request.client.host if request.client else "0.0.0.0")
    user_agent = request.headers.get("User-Agent")
    
    service = AnalyticsService(db)
    
    await service.track_page_view(
        page_type=track_req.page_type or "page",
        tenant_slug=tenant.slug,
        ip_address=ip_address,
        user_agent=user_agent,
        user_id=user.id,
        is_authenticated=True,
    )
    
    return {"success": True}


# ============ Summary Statistics ============

@router.get("/summary", response_model=dict)
async def get_analytics_summary(
    request: Request,
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_tenant_db),
    user = Depends(get_current_user_required),
):
    """Get summary statistics for the last N days"""
    tenant = require_tenant(request)
    
    from app.services.analytics_service import AnalyticsService
    
    service = AnalyticsService(db)
    stats = await service.get_summary_stats(tenant.slug, days)
    
    return {
        "success": True,
        "data": stats
    }


# ============ Daily Statistics ============

@router.get("/daily", response_model=dict)
async def get_daily_stats(
    request: Request,
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_tenant_db),
    user = Depends(get_current_user_required),
):
    """Get daily statistics for the last N days"""
    tenant = require_tenant(request)
    
    from app.services.analytics_service import AnalyticsService
    
    service = AnalyticsService(db)
    daily_stats = await service.get_daily_stats(tenant.slug, days)
    
    return {
        "success": True,
        "data": [
            {
                "date": stat.date.isoformat() if hasattr(stat.date, 'isoformat') else str(stat.date),
                "total_views": stat.total_views,
                "unique_visitors": stat.unique_visitors,
                "authenticated_views": getattr(stat, 'authenticated_views', 0),
                "anonymous_views": getattr(stat, 'anonymous_views', 0),
                "person_views": getattr(stat, 'person_views', 0),
                "branch_views": getattr(stat, 'branch_views', 0),
                "generation_views": getattr(stat, 'generation_views', 0),
                "family_tree_views": getattr(stat, 'family_tree_views', 0),
            }
            for stat in daily_stats
        ]
    }


# ============ Popular Pages ============

@router.get("/popular", response_model=dict)
async def get_popular_pages(
    request: Request,
    page_type: Optional[str] = None,
    days: int = Query(7, ge=1, le=30),
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_tenant_db),
    user = Depends(get_current_user_required),
):
    """Get most viewed pages"""
    tenant = require_tenant(request)
    
    from app.services.analytics_service import AnalyticsService
    
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
