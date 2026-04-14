"""
Analytics service for tracking page views and generating statistics
"""
from datetime import datetime, timezone, timedelta
from typing import Optional
from uuid import UUID

from sqlalchemy import select, func, and_, distinct
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tenant import PageView, DailyVisitStats


class AnalyticsService:
    """Service for analytics and statistics"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def track_page_view(
        self,
        page_type: str,
        tenant_slug: str,
        page_id: Optional[UUID] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        user_id: Optional[UUID] = None,
        is_authenticated: bool = False,
    ) -> PageView:
        """Track a page view"""
        
        # Create page view record
        page_view = PageView(
            page_type=page_type,
            page_id=page_id,
            tenant_slug=tenant_slug,
            ip_address=ip_address,
            user_agent=user_agent,
            user_id=user_id,
            is_authenticated=is_authenticated,
        )
        
        self.db.add(page_view)
        await self.db.flush()
        
        # Update daily statistics (async task in production)
        await self._update_daily_stats(
            tenant_slug=tenant_slug,
            page_type=page_type,
            is_authenticated=is_authenticated,
            ip_address=ip_address,
        )
        
        return page_view
    
    async def _update_daily_stats(
        self,
        tenant_slug: str,
        page_type: str,
        is_authenticated: bool,
        ip_address: Optional[str],
    ):
        """Update daily visit statistics"""
        
        # Get today's date
        today = datetime.now(timezone.utc).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        
        # Get or create daily stats record
        stmt = select(DailyVisitStats).where(
            DailyVisitStats.date == today,
            DailyVisitStats.tenant_slug == tenant_slug
        )
        result = await self.db.execute(stmt)
        stats = result.scalar_one_or_none()
        
        if not stats:
            stats = DailyVisitStats(
                date=today,
                tenant_slug=tenant_slug,
            )
            self.db.add(stats)
            await self.db.flush()
        
        # Update counters
        stats.total_views += 1
        
        if is_authenticated:
            stats.authenticated_views += 1
        else:
            stats.anonymous_views += 1
        
        # Update unique visitors (simplified - in production use Redis)
        if ip_address:
            # This is a simplified approach - production should use Redis for accurate counting
            stats.unique_visitors += 1
        
        # Update page type breakdown
        if page_type == 'person':
            stats.person_views += 1
        elif page_type == 'branch':
            stats.branch_views += 1
        elif page_type == 'generation':
            stats.generation_views += 1
        elif page_type == 'family_tree':
            stats.family_tree_views += 1
        else:
            stats.other_views += 1
    
    async def get_daily_stats(
        self,
        tenant_slug: str,
        days: int = 30,
    ) -> list[DailyVisitStats]:
        """Get daily statistics for the last N days"""
        
        today = datetime.now(timezone.utc).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        start_date = today - timedelta(days=days)
        
        stmt = select(DailyVisitStats).where(
            DailyVisitStats.tenant_slug == tenant_slug,
            DailyVisitStats.date >= start_date,
            DailyVisitStats.date <= today,
        ).order_by(DailyVisitStats.date)
        
        result = await self.db.execute(stmt)
        return result.scalars().all()
    
    async def get_summary_stats(
        self,
        tenant_slug: str,
        days: int = 30,
    ) -> dict:
        """Get summary statistics"""
        
        today = datetime.now(timezone.utc).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        start_date = today - timedelta(days=days)
        
        # Total views
        stmt = select(func.sum(DailyVisitStats.total_views)).where(
            DailyVisitStats.tenant_slug == tenant_slug,
            DailyVisitStats.date >= start_date,
        )
        result = await self.db.execute(stmt)
        total_views = result.scalar() or 0
        
        # Unique visitors
        stmt = select(func.sum(DailyVisitStats.unique_visitors)).where(
            DailyVisitStats.tenant_slug == tenant_slug,
            DailyVisitStats.date >= start_date,
        )
        result = await self.db.execute(stmt)
        unique_visitors = result.scalar() or 0
        
        # Page type breakdown
        stmt = select(
            func.sum(DailyVisitStats.person_views),
            func.sum(DailyVisitStats.branch_views),
            func.sum(DailyVisitStats.generation_views),
            func.sum(DailyVisitStats.family_tree_views),
        ).where(
            DailyVisitStats.tenant_slug == tenant_slug,
            DailyVisitStats.date >= start_date,
        )
        result = await self.db.execute(stmt)
        row = result.first()
        
        return {
            "total_views": total_views,
            "unique_visitors": unique_visitors,
            "person_views": row[0] or 0,
            "branch_views": row[1] or 0,
            "generation_views": row[2] or 0,
            "family_tree_views": row[3] or 0,
            "period_days": days,
        }
    
    async def get_popular_pages(
        self,
        tenant_slug: str,
        page_type: Optional[str] = None,
        days: int = 7,
        limit: int = 10,
    ) -> list[dict]:
        """Get most viewed pages"""
        
        today = datetime.now(timezone.utc).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        start_date = today - timedelta(days=days)
        
        # Build query
        stmt = select(
            PageView.page_id,
            PageView.page_type,
            func.count(PageView.id).label('view_count')
        ).where(
            PageView.tenant_slug == tenant_slug,
            PageView.viewed_at >= start_date,
        )
        
        if page_type:
            stmt = stmt.where(PageView.page_type == page_type)
        
        stmt = stmt.group_by(
            PageView.page_id,
            PageView.page_type,
        ).order_by(
            func.count(PageView.id).desc()
        ).limit(limit)
        
        result = await self.db.execute(stmt)
        rows = result.all()
        
        return [
            {
                "page_id": str(row.page_id) if row.page_id else None,
                "page_type": row.page_type,
                "view_count": row.view_count,
            }
            for row in rows
        ]
