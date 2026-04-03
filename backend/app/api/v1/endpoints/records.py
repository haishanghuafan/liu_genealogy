"""
Genealogy records API endpoints
"""
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel, Field
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_tenant_db
from app.middleware.tenant import require_tenant
from app.middleware.auth import get_current_user_required
from app.models.records import GenealogyRecord, RecordPersonLink

router = APIRouter(prefix="/records", tags=["Records"])


# ============ Schemas ============

class RecordCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    source_type: str = Field("paper", pattern="^(paper|digital|oral)$")
    source_name: Optional[str] = None
    source_url: Optional[str] = None
    page_number: Optional[str] = None
    volume_number: Optional[str] = None
    section: Optional[str] = None
    reliability: str = Field("medium", pattern="^(high|medium|low)$")
    notes: Optional[str] = None


class RecordUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = None
    source_type: Optional[str] = Field(None, pattern="^(paper|digital|oral)$")
    source_name: Optional[str] = None
    page_number: Optional[str] = None
    reliability: Optional[str] = Field(None, pattern="^(high|medium|low)$")
    is_verified: Optional[bool] = None
    notes: Optional[str] = None


class PersonLinkCreate(BaseModel):
    person_id: str
    mention_type: str = Field("mentioned", pattern="^(mentioned|primary|related)$")
    mention_context: Optional[str] = None


# ============ Genealogy Records ============

@router.get("", response_model=dict)
async def list_records(
    request: Request,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    source_type: Optional[str] = None,
    reliability: Optional[str] = None,
    db: AsyncSession = Depends(get_tenant_db),
):
    """List genealogy records"""
    tenant = require_tenant(request)
    
    query = select(GenealogyRecord)
    
    if search:
        query = query.where(
            GenealogyRecord.title.ilike(f"%{search}%") |
            GenealogyRecord.content.ilike(f"%{search}%")
        )
    if source_type:
        query = query.where(GenealogyRecord.source_type == source_type)
    if reliability:
        query = query.where(GenealogyRecord.reliability == reliability)
    
    total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar()
    
    query = query.order_by(GenealogyRecord.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    
    result = await db.execute(query)
    records = result.scalars().all()
    
    return {
        "success": True,
        "data": [{
            "id": str(r.id),
            "title": r.title,
            "content": r.content[:200] + "..." if len(r.content) > 200 else r.content,
            "source_type": r.source_type,
            "source_name": r.source_name,
            "page_number": r.page_number,
            "reliability": r.reliability,
            "is_verified": r.is_verified,
            "created_at": r.created_at.isoformat(),
        } for r in records],
        "meta": {"total": total, "page": page, "page_size": page_size}
    }


@router.post("", response_model=dict)
async def create_record(
    data: RecordCreate,
    request: Request,
    db: AsyncSession = Depends(get_tenant_db),
    user = Depends(get_current_user_required),
):
    """Create a new genealogy record"""
    tenant = require_tenant(request)
    
    record = GenealogyRecord(
        title=data.title,
        content=data.content,
        source_type=data.source_type,
        source_name=data.source_name,
        source_url=data.source_url,
        page_number=data.page_number,
        volume_number=data.volume_number,
        section=data.section,
        reliability=data.reliability,
        notes=data.notes,
        created_by=user.id,
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)
    
    return {"success": True, "data": {"id": str(record.id), "title": record.title}}


@router.get("/{record_id}", response_model=dict)
async def get_record(
    record_id: str,
    request: Request,
    db: AsyncSession = Depends(get_tenant_db),
):
    """Get record details"""
    tenant = require_tenant(request)
    
    stmt = select(GenealogyRecord).where(GenealogyRecord.id == UUID(record_id))
    result = await db.execute(stmt)
    record = result.scalar_one_or_none()
    
    if not record:
        raise HTTPException(404, "记录不存在")
    
    # Get linked persons
    stmt = select(RecordPersonLink).where(RecordPersonLink.record_id == record.id)
    links = (await db.execute(stmt)).scalars().all()
    
    return {
        "success": True,
        "data": {
            "id": str(record.id),
            "title": record.title,
            "content": record.content,
            "source_type": record.source_type,
            "source_name": record.source_name,
            "source_url": record.source_url,
            "source_image": record.source_image,
            "source_pdf": record.source_pdf,
            "page_number": record.page_number,
            "volume_number": record.volume_number,
            "section": record.section,
            "reliability": record.reliability,
            "is_verified": record.is_verified,
            "notes": record.notes,
            "created_at": record.created_at.isoformat(),
            "linked_persons": [
                {"person_id": str(l.person_id), "mention_type": l.mention_type, "context": l.mention_context}
                for l in links
            ],
        }
    }


@router.put("/{record_id}", response_model=dict)
async def update_record(
    record_id: str,
    data: RecordUpdate,
    request: Request,
    db: AsyncSession = Depends(get_tenant_db),
    user = Depends(get_current_user_required),
):
    """Update a genealogy record"""
    tenant = require_tenant(request)
    
    stmt = select(GenealogyRecord).where(GenealogyRecord.id == UUID(record_id))
    result = await db.execute(stmt)
    record = result.scalar_one_or_none()
    
    if not record:
        raise HTTPException(404, "记录不存在")
    
    if data.title is not None:
        record.title = data.title
    if data.content is not None:
        record.content = data.content
    if data.source_type is not None:
        record.source_type = data.source_type
    if data.source_name is not None:
        record.source_name = data.source_name
    if data.page_number is not None:
        record.page_number = data.page_number
    if data.reliability is not None:
        record.reliability = data.reliability
    if data.is_verified is not None:
        record.is_verified = data.is_verified
        if data.is_verified:
            record.verified_by = user.id
            record.verified_at = datetime.now(timezone.utc)
    if data.notes is not None:
        record.notes = data.notes
    
    await db.commit()
    
    return {"success": True, "message": "记录已更新"}


@router.delete("/{record_id}", response_model=dict)
async def delete_record(
    record_id: str,
    request: Request,
    db: AsyncSession = Depends(get_tenant_db),
):
    """Delete a genealogy record"""
    tenant = require_tenant(request)
    
    stmt = select(GenealogyRecord).where(GenealogyRecord.id == UUID(record_id))
    result = await db.execute(stmt)
    record = result.scalar_one_or_none()
    
    if not record:
        raise HTTPException(404, "记录不存在")
    
    await db.delete(record)
    await db.commit()
    
    return {"success": True, "message": "记录已删除"}


# ============ Record-Person Links ============

@router.post("/{record_id}/persons", response_model=dict)
async def link_person_to_record(
    record_id: str,
    data: PersonLinkCreate,
    request: Request,
    db: AsyncSession = Depends(get_tenant_db),
):
    """Link a person to a genealogy record"""
    tenant = require_tenant(request)
    
    link = RecordPersonLink(
        record_id=UUID(record_id),
        person_id=UUID(data.person_id),
        mention_type=data.mention_type,
        mention_context=data.mention_context,
    )
    db.add(link)
    await db.commit()
    
    return {"success": True, "message": "已关联人物"}


@router.delete("/{record_id}/persons/{person_id}", response_model=dict)
async def unlink_person(
    record_id: str,
    person_id: str,
    request: Request,
    db: AsyncSession = Depends(get_tenant_db),
):
    """Remove person link from record"""
    tenant = require_tenant(request)
    
    stmt = select(RecordPersonLink).where(
        and_(
            RecordPersonLink.record_id == UUID(record_id),
            RecordPersonLink.person_id == UUID(person_id),
        )
    )
    result = await db.execute(stmt)
    link = result.scalar_one_or_none()
    
    if not link:
        raise HTTPException(404, "关联不存在")
    
    await db.delete(link)
    await db.commit()
    
    return {"success": True, "message": "已取消关联"}
