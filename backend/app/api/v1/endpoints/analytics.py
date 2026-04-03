"""
Analytics API endpoints
"""
from datetime import date, timedelta
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request
from pydantic import BaseModel, Field
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_tenant_db, get_db
from app.middleware.tenant import require_tenant
from app.middleware.auth import get_current_user_required
from app.models.analytics import DailyVisitStats, PageVisitStats, TenantStats

router = APIRouter(prefix="/analytics", tags=["Analytics"])


# ============ Schemas ============

class VisitTrend(BaseModel):
    date: str
    visits: int
    unique_visitors: int
    unique_ips: int


class PageStats(BaseModel):
    path: str
    total_visits: int
    unique_visitors: int
    last_visit: str


class TenantStatsResponse(BaseModel):
    persons: dict
    generations: dict
    branches: int
    members: dict
    media: dict
    visits: dict
    last_updated: Optional[str]


class AnalyticsDashboardResponse(BaseModel):
    success: bool = True
    data: dict


# ============ Endpoints ============

@router.get("/dashboard", response_model=AnalyticsDashboardResponse)
async def get_dashboard(
    request: Request,
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_tenant_db),
    user = Depends(get_current_user_required),
):
    """Get comprehensive analytics dashboard data"""
    tenant = require_tenant(request)
    
    # Get tenant stats
    from app.services.visit_tracker import visit_tracker
    stats = await visit_tracker.get_tenant_stats(db, tenant.id)
    
    # Get visit trends
    trends = await visit_tracker.get_visit_trends(db, tenant.id, days)
    
    # Get top pages
    top_pages = await _get_top_pages(db, tenant.id, 10)
    
    return AnalyticsDashboardResponse(
        data={
            "stats": stats,
            "trends": trends,
            "top_pages": top_pages,
        }
    )


@router.get("/trends", response_model=dict)
async def get_visit_trends(
    request: Request,
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_tenant_db),
    user = Depends(get_current_user_required),
):
    """Get visit trends for the last N days"""
    tenant = require_tenant(request)
    
    from app.services.visit_tracker import visit_tracker
    trends = await visit_tracker.get_visit_trends(db, tenant.id, days)
    
    return {
        "success": True,
        "data": trends,
        "meta": {
            "days": days,
            "tenant_id": str(tenant.id),
        },
    }


@router.get("/top-pages", response_model=dict)
async def get_top_pages(
    request: Request,
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_tenant_db),
    user = Depends(get_current_user_required),
):
    """Get top visited pages"""
    tenant = require_tenant(request)
    
    pages = await _get_top_pages(db, tenant.id, limit)
    
    return {
        "success": True,
        "data": pages,
    }


@router.get("/realtime", response_model=dict)
async def get_realtime_stats(
    request: Request,
    db: AsyncSession = Depends(get_tenant_db),
    user = Depends(get_current_user_required),
):
    """Get real-time visit statistics (last hour)"""
    tenant = require_tenant(request)
    
    from datetime import datetime, timezone
    from app.models.analytics import PageView
    
    one_hour_ago = datetime.now(timezone.utc) - timedelta(hours=1)
    
    # Get visits in last hour
    stmt = select(func.count()).select_from(PageView).where(
        and_(
            PageView.tenant_id == tenant.id,
            PageView.timestamp >= one_hour_ago,
        )
    )
    result = await db.execute(stmt)
    visits_last_hour = result.scalar() or 0
    
    # Get unique IPs in last hour
    stmt = select(func.count(func.distinct(PageView.ip_address))).select_from(
        PageView
    ).where(
        and_(
            PageView.tenant_id == tenant.id,
            PageView.timestamp >= one_hour_ago,
        )
    )
    result = await db.execute(stmt)
    unique_ips_last_hour = result.scalar() or 0
    
    # Get active users (last 15 min)
    fifteen_min_ago = datetime.now(timezone.utc) - timedelta(minutes=15)
    stmt = select(func.count(func.distinct(PageView.user_id))).select_from(
        PageView
    ).where(
        and_(
            PageView.tenant_id == tenant.id,
            PageView.timestamp >= fifteen_min_ago,
            PageView.user_id != None,
        )
    )
    result = await db.execute(stmt)
    active_users = result.scalar() or 0
    
    return {
        "success": True,
        "data": {
            "visits_last_hour": visits_last_hour,
            "unique_visitors_last_hour": unique_ips_last_hour,
            "active_users": active_users,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    }


# ============ Helper Functions ============

async def _get_top_pages(db: AsyncSession, tenant_id: UUID, limit: int) -> list[dict]:
    """Get top visited pages for a tenant"""
    stmt = select(PageVisitStats).where(
        PageVisitStats.tenant_id == tenant_id
    ).order_by(PageVisitStats.total_visits.desc()).limit(limit)
    
    result = await db.execute(stmt)
    pages = result.scalars().all()
    
    return [
        {
            "path": p.path,
            "total_visits": p.total_visits,
            "unique_visitors": p.unique_visitors,
            "last_visit": p.last_visit.isoformat() if p.last_visit else None,
        }
        for p in pages
    ]
