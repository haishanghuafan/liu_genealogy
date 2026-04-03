"""
Analytics models - visit tracking and statistics
"""
import uuid
from datetime import datetime, date
from typing import Optional

from sqlalchemy import Date, DateTime, String, Integer, Boolean, Index, Text, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class PageView(Base):
    """Page view tracking"""
    
    __tablename__ = "page_views"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    
    # Request info
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    path: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    method: Mapped[str] = mapped_column(String(10), default="GET")
    
    # Client info
    ip_address: Mapped[str] = mapped_column(String(45), nullable=False, index=True)  # IPv6 max 45 chars
    user_agent: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    referer: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    session_key: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # User info (if authenticated)
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True, index=True)
    
    # Tenant context
    tenant_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True, index=True)
    
    # Visit metadata
    is_unique_visit: Mapped[bool] = mapped_column(Boolean, default=False)
    visit_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        index=True,
    )
    
    # Additional metadata
    metadata_json: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    
    __table_args__ = (
        Index("ix_page_views_path_date", "path", "visit_date"),
        Index("ix_page_views_ip_date", "ip_address", "visit_date"),
        Index("ix_page_views_tenant_date", "tenant_id", "visit_date"),
    )
    
    def __repr__(self) -> str:
        return f"<PageView {self.path} - {self.ip_address}>"


class DailyVisitStats(Base):
    """Daily visit statistics"""
    
    __tablename__ = "daily_visit_stats"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    
    date: Mapped[date] = mapped_column(Date, unique=True, nullable=False, index=True)
    tenant_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True, index=True)
    
    # Visit counts
    total_visits: Mapped[int] = mapped_column(Integer, default=0)
    unique_visitors: Mapped[int] = mapped_column(Integer, default=0)
    unique_ips: Mapped[int] = mapped_column(Integer, default=0)
    
    # Page counts
    unique_pages: Mapped[int] = mapped_column(Integer, default=0)
    
    # User counts
    authenticated_visits: Mapped[int] = mapped_column(Integer, default=0)
    anonymous_visits: Mapped[int] = mapped_column(Integer, default=0)
    
    __table_args__ = (
        Index("ix_daily_stats_tenant_date", "tenant_id", "date"),
    )
    
    def __repr__(self) -> str:
        return f"<DailyVisitStats {self.date} - visits:{self.total_visits}>"


class PageVisitStats(Base):
    """Page visit statistics (aggregated)"""
    
    __tablename__ = "page_visit_stats"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    
    path: Mapped[str] = mapped_column(String(500), unique=True, nullable=False, index=True)
    tenant_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True, index=True)
    
    # Visit counts
    total_visits: Mapped[int] = mapped_column(Integer, default=0)
    unique_visitors: Mapped[int] = mapped_column(Integer, default=0)
    
    # Timestamps
    first_visit: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    last_visit: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )
    
    __table_args__ = (
        Index("ix_page_stats_tenant_path", "tenant_id", "path"),
    )
    
    def __repr__(self) -> str:
        return f"<PageVisitStats {self.path} - visits:{self.total_visits}>"


class TenantStats(Base):
    """Tenant-level statistics summary"""
    
    __tablename__ = "tenant_stats"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        unique=True,
        nullable=False,
        index=True,
    )
    
    # Person counts
    total_persons: Mapped[int] = mapped_column(Integer, default=0)
    male_count: Mapped[int] = mapped_column(Integer, default=0)
    female_count: Mapped[int] = mapped_column(Integer, default=0)
    living_count: Mapped[int] = mapped_column(Integer, default=0)
    deceased_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # Generation info
    max_generation: Mapped[int] = mapped_column(Integer, default=0)
    min_generation: Mapped[int] = mapped_column(Integer, default=0)
    
    # Branch info
    branch_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # Member counts
    member_count: Mapped[int] = mapped_column(Integer, default=0)
    admin_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # Media counts
    image_count: Mapped[int] = mapped_column(Integer, default=0)
    storage_used_mb: Mapped[float] = mapped_column(default=0.0)
    
    # Visit stats
    total_visits: Mapped[int] = mapped_column(Integer, default=0)
    visits_today: Mapped[int] = mapped_column(Integer, default=0)
    visits_this_month: Mapped[int] = mapped_column(Integer, default=0)
    
    # Timestamps
    last_updated: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )
    
    def __repr__(self) -> str:
        return f"<TenantStats {self.tenant_id} - persons:{self.total_persons}>"
