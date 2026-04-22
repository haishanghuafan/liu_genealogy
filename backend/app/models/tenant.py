"""
Tenant-level models (each tenant has its own schema)
"""
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    TypeDecorator,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
import json


class JSONType(TypeDecorator):
    """JSON type compatible with both PostgreSQL and SQLite"""
    impl = Text
    cache_ok = True
    
    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            from sqlalchemy.dialects.postgresql import JSONB
            return dialect.type_descriptor(JSONB())
        return dialect.type_descriptor(Text())
    
    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        return json.dumps(value)
    
    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return json.loads(value)

from app.core.database import Base


class Generation(Base):
    """Generation model"""
    
    __tablename__ = "generations"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    number: Mapped[int] = mapped_column(Integer, nullable=False)
    is_spouse: Mapped[bool] = mapped_column(Boolean, default=False)
    name: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    __table_args__ = (
        # UniqueConstraint("number", "is_spouse"),
    )
    
    def __repr__(self) -> str:
        return f"<Generation {self.number}>"


class Branch(Base):
    """Branch model"""
    
    __tablename__ = "branches"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    founder_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    location: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    
    def __repr__(self) -> str:
        return f"<Branch {self.name}>"


class Person(Base):
    """Person model"""
    
    __tablename__ = "persons"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    
    # Basic info
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    courtesy_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    art_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    alias: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    generation_char: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    
    # Gender
    gender: Mapped[str] = mapped_column(String(1), default="M")
    is_outsider: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Generation
    generation_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Parents
    father_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    mother_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    
    # Branch
    branch_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    
    # Birth/Death
    birth_year: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    death_year: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    birth_place: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    lunar_birthday: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # Burial
    burial_place: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)
    burial_fengshui: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    burial_direction: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Biography
    biography: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    achievements: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    descendants_location: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Privacy
    visibility: Mapped[str] = mapped_column(String(20), default="public")
    
    # Order
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    
    # Avatar
    avatar: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    
    def __repr__(self) -> str:
        return f"<Person {self.name}>"
    
    @property
    def full_name(self) -> str:
        parts = [self.name]
        if self.courtesy_name:
            parts.append(f"字{self.courtesy_name}")
        if self.art_name:
            parts.append(f"号{self.art_name}")
        return " ".join(parts)


class SpouseRelation(Base):
    """Spouse relation model"""
    
    __tablename__ = "spouse_relations"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    husband_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    wife_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    
    # 关系类型 - 符合中国传统族谱
    # marriage: 婚姻（正室）, concubine: 妾室, adopted: 继配
    # zhuazhui: 招赘（女招男方）, first-fifth: 一至五房（多妻制）
    relation_type: Mapped[str] = mapped_column(String(20), default="marriage")
    source_info: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)  # 配偶来源信息
    sort_order: Mapped[int] = mapped_column(Integer, default=1)
    
    # UniqueConstraint("husband_id", "wife_id"),
    
    def __repr__(self) -> str:
        return f"<SpouseRelation {self.husband_id} - {self.wife_id}>"


class PersonImage(Base):
    """Person image model"""
    
    __tablename__ = "person_images"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    person_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    title: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    
    def __repr__(self) -> str:
        return f"<PersonImage {self.person_id}>"


class PersonVideo(Base):
    """Person video model"""
    
    __tablename__ = "person_videos"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    person_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    title: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    
    def __repr__(self) -> str:
        return f"<PersonVideo {self.person_id}>"


class PersonAudio(Base):
    """Person audio model - for oral history, interviews, etc."""
    
    __tablename__ = "person_audios"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    person_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    title: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    duration: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # Duration in seconds
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    
    def __repr__(self) -> str:
        return f"<PersonAudio {self.person_id}>"


class ChangeLog(Base):
    """Change log model for audit trail"""
    
    __tablename__ = "change_logs"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    table_name: Mapped[str] = mapped_column(String(50), nullable=False)
    record_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    action: Mapped[str] = mapped_column(String(20), nullable=False)
    old_values: Mapped[Optional[dict]] = mapped_column(JSONType(), nullable=True)
    new_values: Mapped[Optional[dict]] = mapped_column(JSONType(), nullable=True)
    
    changed_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    changed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    
    # Review
    review_status: Mapped[str] = mapped_column(String(20), default="pending")
    reviewed_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    review_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    def __repr__(self) -> str:
        return f"<ChangeLog {self.table_name}:{self.record_id}>"


class PageView(Base):
    """Page view tracking model"""
    
    __tablename__ = "page_views"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    
    # Page info
    page_type: Mapped[str] = mapped_column(String(50), nullable=False)  # person, branch, generation, etc.
    page_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    tenant_slug: Mapped[str] = mapped_column(String(50), nullable=False)
    
    # View info
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    is_authenticated: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Timestamp
    viewed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    
    def __repr__(self) -> str:
        return f"<PageView {self.page_type}:{self.page_id}>"


class DailyVisitStats(Base):
    """Daily visit statistics model"""
    
    __tablename__ = "daily_visit_stats"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    tenant_slug: Mapped[str] = mapped_column(String(50), nullable=False)
    
    # Visit counts
    total_views: Mapped[int] = mapped_column(Integer, default=0)
    unique_visitors: Mapped[int] = mapped_column(Integer, default=0)
    authenticated_views: Mapped[int] = mapped_column(Integer, default=0)
    anonymous_views: Mapped[int] = mapped_column(Integer, default=0)
    
    # Page type breakdown
    person_views: Mapped[int] = mapped_column(Integer, default=0)
    branch_views: Mapped[int] = mapped_column(Integer, default=0)
    generation_views: Mapped[int] = mapped_column(Integer, default=0)
    family_tree_views: Mapped[int] = mapped_column(Integer, default=0)
    other_views: Mapped[int] = mapped_column(Integer, default=0)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )
    
    __table_args__ = (
        # Unique constraint to ensure one record per day per tenant
    )
    
    def __repr__(self) -> str:
        return f"<DailyVisitStats {self.date} - {self.tenant_slug}>"
