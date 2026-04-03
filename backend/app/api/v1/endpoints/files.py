"""
File upload endpoints - media management for tenant
"""
import os
import uuid
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
from app.middleware.tenant import require_tenant, get_tenant

router = APIRouter(prefix="/files", tags=["Files"])


# ============ Schemas ============

class FileUploadResponse(BaseModel):
    """File upload response"""
    id: str
    filename: str
    url: str
    size: int
    mime_type: str
    created_at: str


class FileListResponse(BaseModel):
    success: bool = True
    data: list[FileUploadResponse]
    meta: dict


# ============ Constants ============

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp", "image/svg+xml"}
ALLOWED_VIDEO_TYPES = {"video/mp4", "video/webm", "video/quicktime"}
ALLOWED_DOCUMENT_TYPES = {"application/pdf", "application/msword", 
                           "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                           "application/vnd.ms-excel",
                           "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"}

MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
MAX_STORAGE_MB = 500  # Default limit

# Storage path
DATA_DIR = getattr(settings, "data_dir", None) or "./data"
STORAGE_BASE = Path(DATA_DIR)
MEDIA_DIR = STORAGE_BASE / "media"


# ============ Helper Functions ============

def get_tenant_media_dir(tenant_id: str) -> Path:
    """Get tenant's media directory"""
    dir_path = MEDIA_DIR / tenant_id
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path


def validate_file_type(content_type: str, allowed_types: set) -> bool:
    """Validate file type"""
    return content_type in allowed_types


def get_file_extension(filename: str) -> str:
    """Get file extension"""
    return Path(filename).suffix.lower()


def generate_unique_filename(original_filename: str, tenant_id: str) -> str:
    """Generate unique filename"""
    ext = get_file_extension(original_filename)
    unique_name = f"{tenant_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:8]}{ext}"
    return unique_name


async def check_storage_quota(tenant_id: str, file_size: int, db: AsyncSession) -> bool:
    """Check if tenant has storage quota for the file"""
    # Get current storage usage
    tenant_media_dir = get_tenant_media_dir(tenant_id)
    current_usage = 0
    
    if tenant_media_dir.exists():
        for file in tenant_media_dir.rglob("*"):
            if file.is_file():
                current_usage += file.stat().st_size
    
    # Convert to MB
    current_usage_mb = current_usage / (1024 * 1024)
    
    # Get tenant limit from system
    from app.core.database import db_manager
    system_session = db_manager.get_session_maker("public")
    async with system_session() as sys_db:
        from app.models.system import Tenant as SystemTenant
        stmt = select(SystemTenant).where(SystemTenant.id == tenant_id)
        result = await sys_db.execute(stmt)
        system_tenant = result.scalar_one_or_none()
        
        if system_tenant:
            max_storage = system_tenant.max_storage_mb
        else:
            max_storage = MAX_STORAGE_MB
    
    # Check if new file fits
    new_usage_mb = current_usage_mb + (file_size / (1024 * 1024))
    
    return new_usage_mb <= max_storage


# ============ Endpoints ============

@router.post("/upload", response_model=dict)
async def upload_file(
    request: Request,
    file: UploadFile = File(...),
    category: str = Form("general"),  # general, avatar, person_image, document
    db: AsyncSession = Depends(get_tenant_db),
):
    """Upload a file"""
    tenant = require_tenant(request)
    
    # Validate file size
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)
    
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(400, f"文件大小不能超过 {MAX_FILE_SIZE // (1024*1024)}MB")
    
    # Check storage quota
    if not await check_storage_quota(str(tenant.id), file_size, db):
        raise HTTPException(403, "存储空间不足，请升级套餐或清理文件")
    
    # Validate file type
    content_type = file.content_type
    
    # Determine allowed types based on category
    if category == "avatar":
        allowed_types = ALLOWED_IMAGE_TYPES
    elif category == "person_image":
        allowed_types = ALLOWED_IMAGE_TYPES
    elif category == "video":
        allowed_types = ALLOWED_VIDEO_TYPES
    elif category == "document":
        allowed_types = ALLOWED_DOCUMENT_TYPES
    else:
        allowed_types = ALLOWED_IMAGE_TYPES | ALLOWED_VIDEO_TYPES | ALLOWED_DOCUMENT_TYPES
    
    if not validate_file_type(content_type, allowed_types):
        raise HTTPException(400, f"不支持的文件类型: {content_type}")
    
    # Generate unique filename
    unique_filename = generate_unique_filename(file.filename, str(tenant.id))
    
    # Save file
    tenant_media_dir = get_tenant_media_dir(str(tenant.id))
    file_path = tenant_media_dir / unique_filename
    
    try:
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
    except Exception as e:
        raise HTTPException(500, f"文件保存失败: {str(e)}")
    
    # Generate URL (in production, this would be a CDN URL)
    file_url = f"/api/v1/t/{tenant.slug}/files/{unique_filename}"
    
    return {
        "success": True,
        "data": {
            "id": str(uuid.uuid4()),
            "filename": file.filename,
            "url": file_url,
            "size": file_size,
            "mime_type": content_type,
            "created_at": datetime.now().isoformat(),
        },
    }


@router.get("/{filename}", response_class=FileResponse)
async def get_file(
    filename: str,
    request: Request,
    db: AsyncSession = Depends(get_tenant_db),
):
    """Get/download a file"""
    tenant = require_tenant(request)
    
    file_path = get_tenant_media_dir(str(tenant.id)) / filename
    
    if not file_path.exists():
        raise HTTPException(404, "文件不存在")
    
    return FileResponse(
        path=str(file_path),
        filename=filename,
        media_type="application/octet-stream",
    )


@router.delete("/{file_id}", response_model=dict)
async def delete_file(
    file_id: str,
    request: Request,
    db: AsyncSession = Depends(get_tenant_db),
):
    """Delete a file"""
    tenant = require_tenant(request)
    
    # Note: file_id would need to be mapped to actual filename
    # For now, this is a placeholder - would need a files table to track
    
    return {
        "success": True,
        "message": "文件删除功能需要文件管理模块支持",
    }


@router.get("", response_model=dict)
async def list_files(
    request: Request,
    page: int = 1,
    page_size: int = 20,
    category: Optional[str] = None,
    db: AsyncSession = Depends(get_tenant_db),
):
    """List uploaded files"""
    tenant = require_tenant(request)
    
    tenant_media_dir = get_tenant_media_dir(str(tenant.id))
    
    if not tenant_media_dir.exists():
        return {
            "success": True,
            "data": [],
            "meta": {"total": 0, "page": page, "page_size": page_size},
        }
    
    files = []
    for file_path in tenant_media_dir.iterdir():
        if file_path.is_file():
            stat = file_path.stat()
            files.append({
                "id": file_path.stem,
                "filename": file_path.name,
                "url": f"/api/v1/t/{tenant.slug}/files/{file_path.name}",
                "size": stat.st_size,
                "mime_type": "application/octet-stream",
                "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
            })
    
    # Filter by category (would need actual categorization in production)
    # Paginate
    total = len(files)
    start = (page - 1) * page_size
    end = start + page_size
    paginated_files = files[start:end]
    
    return {
        "success": True,
        "data": paginated_files,
        "meta": {
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
        },
    }


@router.get("/usage", response_model=dict)
async def get_storage_usage(
    request: Request,
    db: AsyncSession = Depends(get_tenant_db),
):
    """Get storage usage statistics"""
    tenant = require_tenant(request)
    
    tenant_media_dir = get_tenant_media_dir(str(tenant.id))
    
    total_size = 0
    file_count = 0
    
    if tenant_media_dir.exists():
        for file in tenant_media_dir.rglob("*"):
            if file.is_file():
                total_size += file.stat().st_size
                file_count += 1
    
    # Get limit from system tenant
    from app.core.database import db_manager
    system_session = db_manager.get_session_maker("public")
    async with system_session() as sys_db:
        from app.models.system import Tenant as SystemTenant
        stmt = select(SystemTenant).where(SystemTenant.id == tenant.id)
        result = await sys_db.execute(stmt)
        system_tenant = result.scalar_one_or_none()
        
        if system_tenant:
            max_storage_mb = system_tenant.max_storage_mb
        else:
            max_storage_mb = MAX_STORAGE_MB
    
    total_size_mb = total_size / (1024 * 1024)
    
    return {
        "success": True,
        "data": {
            "used_mb": round(total_size_mb, 2),
            "max_mb": max_storage_mb,
            "used_percent": round(total_size_mb / max_storage_mb * 100, 1) if max_storage_mb > 0 else 0,
            "file_count": file_count,
        },
    }