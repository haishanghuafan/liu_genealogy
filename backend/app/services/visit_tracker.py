"""
Visit tracking middleware and service
"""
from datetime import datetime, date
from typing import Optional
from uuid import UUID

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import db_manager
from app.models.analytics import PageView, DailyVisitStats, PageVisitStats, TenantStats


class VisitTracker:
    """Service for tracking and aggregating visit statistics"""
    
    # Paths to exclude from tracking
    EXCLUDED_PATHS = [
        "/static/",
        "/media/",
        "/admin/",
        "/favicon.ico",
        "/robots.txt",
        "/sitemap.xml",
        "/api/v1/health",
        "/_next/",
        "/__nextjs",
    ]
    
    @classmethod
    def should_track(cls, path: str) -> bool:
        """Check if path should be tracked"""
        for excluded in cls.EXCLUDED_PATHS:
            if path.startswith(excluded):
                return False
        return True
    
    @classmethod
    def get_client_ip(cls, request) -> str:
        """Get client IP from request"""
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "0.0.0.0"
    
    @classmethod
    async def track_visit(
        cls,
        db: AsyncSession,
        path: str,
        url: str,
        ip_address: str,
        user_id: Optional[UUID] = None,
        tenant_id: Optional[UUID] = None,
        user_agent: Optional[str] = None,
        referer: Optional[str] = None,
        session_key: Optional[str] = None,
    ) -> Optional[PageView]:
        """Track a page visit"""
        if not cls.should_track(path):
            return None
        
        today = date.today()
        
        # Check if unique visit (same IP, same path, same day)
        existing = await db.execute(
            select(PageView).where(
                and_(
                    PageView.path == path,
                    PageView.ip_address == ip_address,
                    PageView.visit_date == today,
                )
            )
        )
        is_unique = existing.scalar_one_or_none() is None
        
        # Create page view record
        page_view = PageView(
            url=url[:500],
            path=path[:500],
            ip_address=ip_address[:45],
            user_agent=user_agent[:500] if user_agent else None,
            referer=referer[:500] if referer else None,
            session_key=session_key[:100] if session_key else None,
            user_id=user_id,
            tenant_id=tenant_id,
            is_unique_visit=is_unique,
            visit_date=today,
        )
        
        db.add(page_view)
        
        # Update daily stats
        await cls.update_daily_stats(db, today, tenant_id)
        
        # Update page stats
        await cls.update_page_stats(db, path, tenant_id)
        
        await db.commit()
        return page_view
    
    @classmethod
    async def update_daily_stats(
        cls,
        db: AsyncSession,
        visit_date: date,
        tenant_id: Optional[UUID] = None,
    ):
        """Update daily visit statistics"""
        # Get or create daily stats record
        stmt = select(DailyVisitStats).where(
            and_(
                DailyVisitStats.date == visit_date,
                DailyVisitStats.tenant_id == tenant_id,
            )
        )
        result = await db.execute(stmt)
        stats = result.scalar_one_or_none()
        
        if not stats:
            stats = DailyVisitStats(
                date=visit_date,
                tenant_id=tenant_id,
            )
            db.add(stats)
        
        # Calculate stats
        base_query = select(PageView).where(PageView.visit_date == visit_date)
        if tenant_id:
            base_query = base_query.where(PageView.tenant_id == tenant_id)
        
        # Total visits
        total = await db.execute(select(func.count()).select_from(base_query.subquery()))
        stats.total_visits = total.scalar() or 0
        
        # Unique visitors
        unique = await db.execute(
            select(func.count()).select_from(
                base_query.where(PageView.is_unique_visit == True).subquery()
            )
        )
        stats.unique_visitors = unique.scalar() or 0
        
        # Unique IPs
        unique_ips = await db.execute(
            select(func.count(func.distinct(PageView.ip_address))).select_from(
                base_query.subquery()
            )
        )
        stats.unique_ips = unique_ips.scalar() or 0
        
        # Authenticated vs anonymous
        auth_visits = await db.execute(
            select(func.count()).select_from(
                base_query.where(PageView.user_id != None).subquery()
            )
        )
        stats.authenticated_visits = auth_visits.scalar() or 0
        stats.anonymous_visits = stats.total_visits - stats.authenticated_visits
    
    @classmethod
    async def update_page_stats(
        cls,
        db: AsyncSession,
        path: str,
        tenant_id: Optional[UUID] = None,
    ):
        """Update page visit statistics"""
        stmt = select(PageVisitStats).where(
            and_(
                PageVisitStats.path == path,
                PageVisitStats.tenant_id == tenant_id,
            )
        )
        result = await db.execute(stmt)
        stats = result.scalar_one_or_none()
        
        if not stats:
            stats = PageVisitStats(
                path=path,
                tenant_id=tenant_id,
            )
            db.add(stats)
        
        # Calculate stats
        base_query = select(PageView).where(PageView.path == path)
        if tenant_id:
            base_query = base_query.where(PageView.tenant_id == tenant_id)
        
        total = await db.execute(select(func.count()).select_from(base_query.subquery()))
        stats.total_visits = total.scalar() or 0
        
        unique = await db.execute(
            select(func.count()).select_from(
                base_query.where(PageView.is_unique_visit == True).subquery()
            )
        )
        stats.unique_visitors = unique.scalar() or 0
    
    @classmethod
    async def get_tenant_stats(
        cls,
        db: AsyncSession,
        tenant_id: UUID,
    ) -> dict:
        """Get comprehensive tenant statistics"""
        # Get tenant stats record
        stmt = select(TenantStats).where(TenantStats.tenant_id == tenant_id)
        result = await db.execute(stmt)
        stats = result.scalar_one_or_none()
        
        if not stats:
            # Create new stats record
            stats = TenantStats(tenant_id=tenant_id)
            db.add(stats)
            await db.commit()
            await db.refresh(stats)
        
        return {
            "persons": {
                "total": stats.total_persons,
                "male": stats.male_count,
                "female": stats.female_count,
                "living": stats.living_count,
                "deceased": stats.deceased_count,
            },
            "generations": {
                "max": stats.max_generation,
                "min": stats.min_generation,
                "span": stats.max_generation - stats.min_generation + 1 if stats.max_generation else 0,
            },
            "branches": stats.branch_count,
            "members": {
                "total": stats.member_count,
                "admins": stats.admin_count,
            },
            "media": {
                "images": stats.image_count,
                "storage_mb": round(stats.storage_used_mb, 2),
            },
            "visits": {
                "total": stats.total_visits,
                "today": stats.visits_today,
                "this_month": stats.visits_this_month,
            },
            "last_updated": stats.last_updated.isoformat() if stats.last_updated else None,
        }
    
    @classmethod
    async def get_visit_trends(
        cls,
        db: AsyncSession,
        tenant_id: Optional[UUID] = None,
        days: int = 30,
    ) -> list[dict]:
        """Get visit trends for the last N days"""
        from datetime import timedelta
        
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        stmt = select(DailyVisitStats).where(
            and_(
                DailyVisitStats.date >= start_date,
                DailyVisitStats.date <= end_date,
                DailyVisitStats.tenant_id == tenant_id,
            )
        ).order_by(DailyVisitStats.date)
        
        result = await db.execute(stmt)
        stats = result.scalars().all()
        
        return [
            {
                "date": s.date.isoformat(),
                "visits": s.total_visits,
                "unique_visitors": s.unique_visitors,
                "unique_ips": s.unique_ips,
            }
            for s in stats
        ]


# Singleton instance
visit_tracker = VisitTracker()
