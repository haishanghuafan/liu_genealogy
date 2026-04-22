"""
Genealogy record model - original genealogy data source
"""
import json
from datetime import datetime
from typing import Optional

import sqlalchemy
from sqlalchemy import DateTime, String, Integer, Text, ForeignKey, TypeDecorator, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.core.uuid7 import generate_uuid


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


class GenealogyRecord(Base):
    """Original genealogy record (from paper/digital source)"""

    __tablename__ = "genealogy_records"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=generate_uuid,
    )

    # Basic info
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)

    # Source info
    source_type: Mapped[str] = mapped_column(String(50), default="paper")  # paper, digital, oral
    source_name: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)
    source_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Image/PDF source
    source_image: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    source_pdf: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Location info
    page_number: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    volume_number: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    section: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Reliability
    reliability: Mapped[str] = mapped_column(String(20), default="medium")
    is_verified: Mapped[bool] = mapped_column(default=False)
    verified_by: Mapped[Optional[UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Notes
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Metadata
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )
    created_by: Mapped[Optional[UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)

    def __repr__(self) -> str:
        return f"<GenealogyRecord {self.title}>"


class RecordPersonLink(Base):
    """Link between genealogy records and persons"""

    __tablename__ = "record_person_links"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=generate_uuid,
    )

    record_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("genealogy_records.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    person_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
    )
    
    mention_type: Mapped[str] = mapped_column(String(50), default="mentioned")
    mention_context: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    
    def __repr__(self) -> str:
        return f"<RecordPersonLink {self.record_id}:{self.person_id}>"
