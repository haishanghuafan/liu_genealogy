"""
Person media API endpoints - images, videos, audio uploads
"""
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Request, Form
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_tenant_db
from app.core.uuid7 import uuid7_str
from app.middleware.tenant import require_tenant, get_tenant
from app.models.tenant import Person, PersonImage, PersonVideo, PersonAudio
from app.services.quota_service import quota_service

router = APIRouter(prefix="/persons", tags=["Person Media"])


# ============ Constants ============

# File size limits (in bytes)
MAX_AVATAR_SIZE = 5 * 1024 * 1024      # 5MB
MAX_IMAGE_SIZE = 10 * 1024 * 1024      # 10MB
MAX_AUDIO_SIZE = 50 * 1024 * 1024      # 50MB
MAX_VIDEO_SIZE = 100 * 1024 * 1024     # 100MB

# Allowed MIME types
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}
ALLOWED_AUDIO_TYPES = {"audio/mpeg", "audio/mp3", "audio/wav", "audio/ogg", "audio/aac"}
ALLOWED_VIDEO_TYPES = {"video/mp4", "video/webm", "video/quicktime", "video/x-msvideo"}

# Storage path
DATA_DIR = getattr(settings, "data_dir", None) or "./data"
STORAGE_BASE = Path(DATA_DIR)
MEDIA_DIR = STORAGE_BASE / "person_media"


# ============ Schemas ============

class MediaUploadResponse(BaseModel):
    """Media upload response"""
    id: str
    person_id: str
    type: str  # image, video, audio
    url: str
    title: Optional[str] = None
    description: Optional[str] = None
    size: int
    mime_type: str
    created_at: str


class MediaListResponse(BaseModel):
    success: bool = True
    data: list[MediaUploadResponse]


class MediaDeleteResponse(BaseModel):
    success: bool = True
    message: str


# ============ Helper Functions ============

def get_person_media_dir(tenant_id: str, person_id: str) -> Path:
    """Get person's media directory"""
    dir_path = MEDIA_DIR / tenant_id / person_id
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path


def validate_file_type(content_type: str, allowed_types: set) -> bool:
    """Validate file type"""
    return content_type in allowed_types


def generate_unique_filename(original_filename: str) -> str:
    """Generate unique filename"""
    ext = Path(original_filename).suffix.lower()
    unique_name = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid7_str()[:8]}{ext}"
    return unique_name


async def check_storage_quota_with_file(
    tenant,
    file_size: int,
    db: AsyncSession
) -> bool:
    """Check if tenant has enough storage quota for the file"""
    # Get current storage usage
    tenant_media_dir = MEDIA_DIR / str(tenant.id)
    current_usage = 0
    
    if tenant_media_dir.exists():
        for file in tenant_media_dir.rglob("*"):
            if file.is_file():
                current_usage += file.stat().st_size
    
    # Convert to MB
    current_usage_mb = current_usage / (1024 * 1024)
    new_file_mb = file_size / (1024 * 1024)
    
    # Check quota
    quota_result = await quota_service.check_storage_quota(
        tenant.plan,
        current_usage_mb
    )
    
    if not quota_result.allowed:
        return False
    
    # Check if new file fits
    limit_bytes = quota_result.limit * 1024 * 1024 if quota_result.limit > 0 else float('inf')
    return (current_usage + file_size) <= limit_bytes


# ============ Avatar Endpoints ============

@router.post("/{person_id}/avatar", response_model=dict)
async def upload_avatar(
    request: Request,
    person_id: str,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_tenant_db),
):
    """Upload or update person's avatar"""
    tenant = require_tenant(request)
    
    # Validate file size
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)
    
    if file_size > MAX_AVATAR_SIZE:
        raise HTTPException(400, f"头像大小不能超过 {MAX_AVATAR_SIZE // (1024*1024)}MB")
    
    # Validate file type
    if not validate_file_type(file.content_type, ALLOWED_IMAGE_TYPES):
        raise HTTPException(400, f"不支持的图片格式: {file.content_type}")
    
    # Check storage quota
    if not await check_storage_quota_with_file(tenant, file_size, db):
        raise HTTPException(403, "存储空间不足，请升级套餐或清理文件")
    
    # Verify person exists
    stmt = select(Person).where(Person.id == uuid.UUID(person_id))
    result = await db.execute(stmt)
    person = result.scalar_one_or_none()
    
    if not person:
        raise HTTPException(404, "人物不存在")
    
    # Generate unique filename
    unique_filename = generate_unique_filename(file.filename)
    
    # Save file
    person_media_dir = get_person_media_dir(str(tenant.id), person_id)
    file_path = person_media_dir / unique_filename
    
    try:
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
    except Exception as e:
        raise HTTPException(500, f"文件保存失败: {str(e)}")
    
    # Delete old avatar if exists
    if person.avatar:
        old_path = person_media_dir / Path(person.avatar).name
        if old_path.exists():
            old_path.unlink()
    
    # Update person's avatar
    file_url = f"/api/v1/t/{tenant.slug}/persons/{person_id}/media/{unique_filename}"
    person.avatar = file_url
    await db.commit()
    
    return {
        "success": True,
        "data": {
            "url": file_url,
            "size": file_size,
            "mime_type": file.content_type,
        },
    }


@router.delete("/{person_id}/avatar", response_model=dict)
async def delete_avatar(
    request: Request,
    person_id: str,
    db: AsyncSession = Depends(get_tenant_db),
):
    """Delete person's avatar"""
    tenant = require_tenant(request)
    
    # Verify person exists
    stmt = select(Person).where(Person.id == uuid.UUID(person_id))
    result = await db.execute(stmt)
    person = result.scalar_one_or_none()
    
    if not person:
        raise HTTPException(404, "人物不存在")
    
    # Delete avatar file if exists
    if person.avatar:
        person_media_dir = get_person_media_dir(str(tenant.id), person_id)
        old_path = person_media_dir / Path(person.avatar).name
        if old_path.exists():
            old_path.unlink()
        
        person.avatar = None
        await db.commit()
    
    return {
        "success": True,
        "message": "头像已删除",
    }


# ============ Image Endpoints ============

@router.post("/{person_id}/images", response_model=dict)
async def upload_image(
    request: Request,
    person_id: str,
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_tenant_db),
):
    """Upload an image for a person"""
    tenant = require_tenant(request)
    
    # Validate file size
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)
    
    if file_size > MAX_IMAGE_SIZE:
        raise HTTPException(400, f"图片大小不能超过 {MAX_IMAGE_SIZE // (1024*1024)}MB")
    
    # Validate file type
    if not validate_file_type(file.content_type, ALLOWED_IMAGE_TYPES):
        raise HTTPException(400, f"不支持的图片格式: {file.content_type}")
    
    # Check storage quota
    if not await check_storage_quota_with_file(tenant, file_size, db):
        raise HTTPException(403, "存储空间不足，请升级套餐或清理文件")
    
    # Verify person exists
    stmt = select(Person).where(Person.id == uuid.UUID(person_id))
    result = await db.execute(stmt)
    person = result.scalar_one_or_none()
    
    if not person:
        raise HTTPException(404, "人物不存在")
    
    # Generate unique filename
    unique_filename = generate_unique_filename(file.filename)
    
    # Save file
    person_media_dir = get_person_media_dir(str(tenant.id), person_id)
    file_path = person_media_dir / unique_filename
    
    try:
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
    except Exception as e:
        raise HTTPException(500, f"文件保存失败: {str(e)}")
    
    # Create image record
    file_url = f"/api/v1/t/{tenant.slug}/persons/{person_id}/media/{unique_filename}"
    image = PersonImage(
        person_id=uuid.UUID(person_id),
        url=file_url,
        title=title,
        description=description,
    )
    db.add(image)
    await db.commit()
    await db.refresh(image)
    
    return {
        "success": True,
        "data": {
            "id": str(image.id),
            "person_id": person_id,
            "type": "image",
            "url": file_url,
            "title": title,
            "description": description,
            "size": file_size,
            "mime_type": file.content_type,
            "created_at": image.created_at.isoformat(),
        },
    }


@router.get("/{person_id}/images", response_model=dict)
async def list_images(
    request: Request,
    person_id: str,
    db: AsyncSession = Depends(get_tenant_db),
):
    """List all images for a person"""
    require_tenant(request)
    
    stmt = select(PersonImage).where(
        PersonImage.person_id == uuid.UUID(person_id)
    ).order_by(PersonImage.sort_order, PersonImage.created_at.desc())
    
    result = await db.execute(stmt)
    images = result.scalars().all()
    
    return {
        "success": True,
        "data": [
            {
                "id": str(img.id),
                "person_id": person_id,
                "type": "image",
                "url": img.url,
                "title": img.title,
                "description": img.description,
                "created_at": img.created_at.isoformat(),
            }
            for img in images
        ],
    }


@router.delete("/{person_id}/images/{image_id}", response_model=dict)
async def delete_image(
    request: Request,
    person_id: str,
    image_id: str,
    db: AsyncSession = Depends(get_tenant_db),
):
    """Delete an image"""
    tenant = require_tenant(request)
    
    stmt = select(PersonImage).where(
        and_(
            PersonImage.id == uuid.UUID(image_id),
            PersonImage.person_id == uuid.UUID(person_id)
        )
    )
    result = await db.execute(stmt)
    image = result.scalar_one_or_none()
    
    if not image:
        raise HTTPException(404, "图片不存在")
    
    # Delete file
    person_media_dir = get_person_media_dir(str(tenant.id), person_id)
    file_path = person_media_dir / Path(image.url).name
    if file_path.exists():
        file_path.unlink()
    
    # Delete record
    await db.delete(image)
    await db.commit()
    
    return {
        "success": True,
        "message": "图片已删除",
    }


# ============ Video Endpoints ============

@router.post("/{person_id}/videos", response_model=dict)
async def upload_video(
    request: Request,
    person_id: str,
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_tenant_db),
):
    """Upload a video for a person"""
    tenant = require_tenant(request)
    
    # Validate file size
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)
    
    if file_size > MAX_VIDEO_SIZE:
        raise HTTPException(400, f"视频大小不能超过 {MAX_VIDEO_SIZE // (1024*1024)}MB")
    
    # Validate file type
    if not validate_file_type(file.content_type, ALLOWED_VIDEO_TYPES):
        raise HTTPException(400, f"不支持的视频格式: {file.content_type}")
    
    # Check storage quota
    if not await check_storage_quota_with_file(tenant, file_size, db):
        raise HTTPException(403, "存储空间不足，请升级套餐或清理文件")
    
    # Verify person exists
    stmt = select(Person).where(Person.id == uuid.UUID(person_id))
    result = await db.execute(stmt)
    person = result.scalar_one_or_none()
    
    if not person:
        raise HTTPException(404, "人物不存在")
    
    # Generate unique filename
    unique_filename = generate_unique_filename(file.filename)
    
    # Save file
    person_media_dir = get_person_media_dir(str(tenant.id), person_id)
    file_path = person_media_dir / unique_filename
    
    try:
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
    except Exception as e:
        raise HTTPException(500, f"文件保存失败: {str(e)}")
    
    # Create video record
    file_url = f"/api/v1/t/{tenant.slug}/persons/{person_id}/media/{unique_filename}"
    video = PersonVideo(
        person_id=uuid.UUID(person_id),
        url=file_url,
        title=title,
        description=description,
    )
    db.add(video)
    await db.commit()
    await db.refresh(video)
    
    return {
        "success": True,
        "data": {
            "id": str(video.id),
            "person_id": person_id,
            "type": "video",
            "url": file_url,
            "title": title,
            "description": description,
            "size": file_size,
            "mime_type": file.content_type,
            "created_at": video.created_at.isoformat(),
        },
    }


@router.get("/{person_id}/videos", response_model=dict)
async def list_videos(
    request: Request,
    person_id: str,
    db: AsyncSession = Depends(get_tenant_db),
):
    """List all videos for a person"""
    require_tenant(request)
    
    stmt = select(PersonVideo).where(
        PersonVideo.person_id == uuid.UUID(person_id)
    ).order_by(PersonVideo.created_at.desc())
    
    result = await db.execute(stmt)
    videos = result.scalars().all()
    
    return {
        "success": True,
        "data": [
            {
                "id": str(vid.id),
                "person_id": person_id,
                "type": "video",
                "url": vid.url,
                "title": vid.title,
                "description": vid.description,
                "created_at": vid.created_at.isoformat(),
            }
            for vid in videos
        ],
    }


@router.delete("/{person_id}/videos/{video_id}", response_model=dict)
async def delete_video(
    request: Request,
    person_id: str,
    video_id: str,
    db: AsyncSession = Depends(get_tenant_db),
):
    """Delete a video"""
    tenant = require_tenant(request)
    
    stmt = select(PersonVideo).where(
        and_(
            PersonVideo.id == uuid.UUID(video_id),
            PersonVideo.person_id == uuid.UUID(person_id)
        )
    )
    result = await db.execute(stmt)
    video = result.scalar_one_or_none()
    
    if not video:
        raise HTTPException(404, "视频不存在")
    
    # Delete file
    person_media_dir = get_person_media_dir(str(tenant.id), person_id)
    file_path = person_media_dir / Path(video.url).name
    if file_path.exists():
        file_path.unlink()
    
    # Delete record
    await db.delete(video)
    await db.commit()
    
    return {
        "success": True,
        "message": "视频已删除",
    }


# ============ Audio Endpoints ============

@router.post("/{person_id}/audios", response_model=dict)
async def upload_audio(
    request: Request,
    person_id: str,
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    duration: Optional[int] = Form(None),
    db: AsyncSession = Depends(get_tenant_db),
):
    """Upload an audio file for a person (oral history, interviews, etc.)"""
    tenant = require_tenant(request)
    
    # Validate file size
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)
    
    if file_size > MAX_AUDIO_SIZE:
        raise HTTPException(400, f"音频大小不能超过 {MAX_AUDIO_SIZE // (1024*1024)}MB")
    
    # Validate file type
    if not validate_file_type(file.content_type, ALLOWED_AUDIO_TYPES):
        raise HTTPException(400, f"不支持的音频格式: {file.content_type}")
    
    # Check storage quota
    if not await check_storage_quota_with_file(tenant, file_size, db):
        raise HTTPException(403, "存储空间不足，请升级套餐或清理文件")
    
    # Verify person exists
    stmt = select(Person).where(Person.id == uuid.UUID(person_id))
    result = await db.execute(stmt)
    person = result.scalar_one_or_none()
    
    if not person:
        raise HTTPException(404, "人物不存在")
    
    # Generate unique filename
    unique_filename = generate_unique_filename(file.filename)
    
    # Save file
    person_media_dir = get_person_media_dir(str(tenant.id), person_id)
    file_path = person_media_dir / unique_filename
    
    try:
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
    except Exception as e:
        raise HTTPException(500, f"文件保存失败: {str(e)}")
    
    # Create audio record
    file_url = f"/api/v1/t/{tenant.slug}/persons/{person_id}/media/{unique_filename}"
    audio = PersonAudio(
        person_id=uuid.UUID(person_id),
        url=file_url,
        title=title,
        description=description,
        duration=duration,
    )
    db.add(audio)
    await db.commit()
    await db.refresh(audio)
    
    return {
        "success": True,
        "data": {
            "id": str(audio.id),
            "person_id": person_id,
            "type": "audio",
            "url": file_url,
            "title": title,
            "description": description,
            "duration": duration,
            "size": file_size,
            "mime_type": file.content_type,
            "created_at": audio.created_at.isoformat(),
        },
    }


@router.get("/{person_id}/audios", response_model=dict)
async def list_audios(
    request: Request,
    person_id: str,
    db: AsyncSession = Depends(get_tenant_db),
):
    """List all audio files for a person"""
    require_tenant(request)
    
    stmt = select(PersonAudio).where(
        PersonAudio.person_id == uuid.UUID(person_id)
    ).order_by(PersonAudio.created_at.desc())
    
    result = await db.execute(stmt)
    audios = result.scalars().all()
    
    return {
        "success": True,
        "data": [
            {
                "id": str(audio.id),
                "person_id": person_id,
                "type": "audio",
                "url": audio.url,
                "title": audio.title,
                "description": audio.description,
                "duration": audio.duration,
                "created_at": audio.created_at.isoformat(),
            }
            for audio in audios
        ],
    }


@router.delete("/{person_id}/audios/{audio_id}", response_model=dict)
async def delete_audio(
    request: Request,
    person_id: str,
    audio_id: str,
    db: AsyncSession = Depends(get_tenant_db),
):
    """Delete an audio file"""
    tenant = require_tenant(request)
    
    stmt = select(PersonAudio).where(
        and_(
            PersonAudio.id == uuid.UUID(audio_id),
            PersonAudio.person_id == uuid.UUID(person_id)
        )
    )
    result = await db.execute(stmt)
    audio = result.scalar_one_or_none()
    
    if not audio:
        raise HTTPException(404, "音频不存在")
    
    # Delete file
    person_media_dir = get_person_media_dir(str(tenant.id), person_id)
    file_path = person_media_dir / Path(audio.url).name
    if file_path.exists():
        file_path.unlink()
    
    # Delete record
    await db.delete(audio)
    await db.commit()
    
    return {
        "success": True,
        "message": "音频已删除",
    }


# ============ Combined Media Endpoints ============

@router.get("/{person_id}/media", response_model=dict)
async def list_all_media(
    request: Request,
    person_id: str,
    db: AsyncSession = Depends(get_tenant_db),
):
    """List all media (images, videos, audios) for a person"""
    require_tenant(request)
    
    # Get images
    img_stmt = select(PersonImage).where(
        PersonImage.person_id == uuid.UUID(person_id)
    ).order_by(PersonImage.sort_order, PersonImage.created_at.desc())
    
    # Get videos
    vid_stmt = select(PersonVideo).where(
        PersonVideo.person_id == uuid.UUID(person_id)
    ).order_by(PersonVideo.created_at.desc())
    
    # Get audios
    aud_stmt = select(PersonAudio).where(
        PersonAudio.person_id == uuid.UUID(person_id)
    ).order_by(PersonAudio.created_at.desc())
    
    img_result = await db.execute(img_stmt)
    vid_result = await db.execute(vid_stmt)
    aud_result = await db.execute(aud_stmt)
    
    images = img_result.scalars().all()
    videos = vid_result.scalars().all()
    audios = aud_result.scalars().all()
    
    all_media = []
    
    for img in images:
        all_media.append({
            "id": str(img.id),
            "type": "image",
            "url": img.url,
            "title": img.title,
            "description": img.description,
            "created_at": img.created_at.isoformat(),
        })
    
    for vid in videos:
        all_media.append({
            "id": str(vid.id),
            "type": "video",
            "url": vid.url,
            "title": vid.title,
            "description": vid.description,
            "created_at": vid.created_at.isoformat(),
        })
    
    for audio in audios:
        all_media.append({
            "id": str(audio.id),
            "type": "audio",
            "url": audio.url,
            "title": audio.title,
            "description": audio.description,
            "duration": audio.duration,
            "created_at": audio.created_at.isoformat(),
        })
    
    # Sort by created_at desc
    all_media.sort(key=lambda x: x["created_at"], reverse=True)
    
    return {
        "success": True,
        "data": all_media,
    }


@router.get("/{person_id}/media/{filename}", response_class=FileResponse)
async def get_media_file(
    request: Request,
    person_id: str,
    filename: str,
    db: AsyncSession = Depends(get_tenant_db),
):
    """Get/serve a media file"""
    tenant = require_tenant(request)
    
    person_media_dir = get_person_media_dir(str(tenant.id), person_id)
    file_path = person_media_dir / filename
    
    if not file_path.exists():
        raise HTTPException(404, "文件不存在")
    
    return FileResponse(
        path=str(file_path),
        filename=filename,
        media_type="application/octet-stream",
    )
