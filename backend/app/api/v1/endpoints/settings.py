"""
Family settings endpoints - tenant configuration management
"""
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel, Field
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_tenant_db
from app.middleware.tenant import require_tenant
from app.models.system import Tenant

router = APIRouter(prefix="/settings", tags=["Settings"])


# ============ Schemas ============

class TenantSettingsUpdate(BaseModel):
    """Update tenant settings"""
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    logo: Optional[str] = Field(None, max_length=500)
    cover_image: Optional[str] = Field(None, max_length=500)
    
    # Privacy settings
    allow_public_search: Optional[bool] = None
    require_login_for_details: Optional[bool] = None
    
    # Display settings
    tree_layout: Optional[str] = Field(None, pattern="^(vertical|horizontal|radial)$")
    default_generation_view: Optional[str] = Field(None, pattern="^(list|tree|grid)$")
    
    # Feature toggles
    enable_family_tree: Optional[bool] = None
    enable_photo_gallery: Optional[bool] = None
    enable_timeline: Optional[bool] = None
    enable_messages: Optional[bool] = None


class TenantSettingsResponse(BaseModel):
    """Tenant settings response"""
    id: str
    name: str
    slug: str
    surname: str
    description: Optional[str]
    logo: Optional[str]
    cover_image: Optional[str]
    
    # Subscription
    plan: str
    max_persons: int
    max_members: int
    max_storage_mb: int
    
    # Privacy
    is_public: bool
    allow_public_search: bool
    require_login_for_details: bool
    
    # Display
    tree_layout: str
    default_generation_view: str
    
    # Features
    enable_family_tree: bool
    enable_photo_gallery: bool
    enable_timeline: bool
    enable_messages: bool
    
    # Timestamps
    created_at: str
    updated_at: str
    
    class Config:
        from_attributes = True


class PrivacySettingsUpdate(BaseModel):
    """Privacy settings update"""
    visibility_default: str = Field("public", pattern="^(public|member|private)$")
    allow_guest_search: bool = True
    show_generation_numbers: bool = True
    show_birth_dates: bool = True
    show_death_dates: bool = True
    show_contact_info: bool = False


class DisplaySettingsUpdate(BaseModel):
    """Display settings update"""
    theme: str = Field("light", pattern="^(light|dark|auto)$")
    language: str = Field("zh-CN", pattern="^(zh-CN|en-US)$")
    date_format: str = Field("YYYY-MM-DD", pattern="^(YYYY-MM-DD|DD-MM-YYYY|MM-DD-YYYY)$")
    tree_direction: str = Field("vertical", pattern="^(vertical|horizontal)$")
    show_photos: bool = True
    show_dates: bool = True


# ============ Endpoints ============

@router.get("", response_model=dict)
async def get_tenant_settings(
    request: Request,
    db: AsyncSession = Depends(get_tenant_db),
):
    """Get current tenant settings"""
    tenant = require_tenant(request)
    
    # Get system-level tenant info for subscription details
    from app.core.database import db_manager
    system_session = db_manager.get_session_maker("public")
    async with system_session() as sys_db:
        from app.models.system import Tenant as SystemTenant
        stmt = select(SystemTenant).where(SystemTenant.id == tenant.id)
        result = await sys_db.execute(stmt)
        system_tenant = result.scalar_one_or_none()
    
    settings = tenant.settings or {}
    
    return {
        "success": True,
        "data": {
            "id": str(tenant.id),
            "name": tenant.name,
            "slug": tenant.slug,
            "surname": tenant.surname,
            "description": settings.get("description"),
            "logo": settings.get("logo"),
            "cover_image": settings.get("cover_image"),
            
            # Subscription (from system tenant)
            "plan": system_tenant.plan if system_tenant else "free",
            "max_persons": system_tenant.max_persons if system_tenant else 100,
            "max_members": system_tenant.max_members if system_tenant else 5,
            "max_storage_mb": system_tenant.max_storage_mb if system_tenant else 100,
            
            # Privacy
            "is_public": tenant.is_public,
            "allow_public_search": settings.get("allow_public_search", True),
            "require_login_for_details": settings.get("require_login_for_details", False),
            
            # Display
            "tree_layout": settings.get("tree_layout", "vertical"),
            "default_generation_view": settings.get("default_generation_view", "tree"),
            
            # Features
            "enable_family_tree": settings.get("enable_family_tree", True),
            "enable_photo_gallery": settings.get("enable_photo_gallery", True),
            "enable_timeline": settings.get("enable_timeline", True),
            "enable_messages": settings.get("enable_messages", False),
            
            "created_at": tenant.created_at.isoformat(),
            "updated_at": tenant.updated_at.isoformat(),
        },
    }


@router.put("", response_model=dict)
async def update_tenant_settings(
    data: TenantSettingsUpdate,
    request: Request,
    db: AsyncSession = Depends(get_tenant_db),
):
    """Update tenant settings"""
    tenant = require_tenant(request)
    
    # Get current settings
    settings = tenant.settings or {}
    
    # Update fields
    if data.name is not None:
        tenant.name = data.name
    if data.description is not None:
        settings["description"] = data.description
    if data.logo is not None:
        settings["logo"] = data.logo
    if data.cover_image is not None:
        settings["cover_image"] = data.cover_image
    
    if data.allow_public_search is not None:
        settings["allow_public_search"] = data.allow_public_search
    if data.require_login_for_details is not None:
        settings["require_login_for_details"] = data.require_login_for_details
    
    if data.tree_layout is not None:
        settings["tree_layout"] = data.tree_layout
    if data.default_generation_view is not None:
        settings["default_generation_view"] = data.default_generation_view
    
    if data.enable_family_tree is not None:
        settings["enable_family_tree"] = data.enable_family_tree
    if data.enable_photo_gallery is not None:
        settings["enable_photo_gallery"] = data.enable_photo_gallery
    if data.enable_timeline is not None:
        settings["enable_timeline"] = data.enable_timeline
    if data.enable_messages is not None:
        settings["enable_messages"] = data.enable_messages
    
    tenant.settings = settings
    await db.commit()
    await db.refresh(tenant)
    
    return {
        "success": True,
        "message": "设置已更新",
        "data": settings,
    }


@router.get("/privacy", response_model=dict)
async def get_privacy_settings(
    request: Request,
    db: AsyncSession = Depends(get_tenant_db),
):
    """Get privacy settings"""
    tenant = require_tenant(request)
    settings = tenant.settings or {}
    
    return {
        "success": True,
        "data": {
            "visibility_default": settings.get("visibility_default", "public"),
            "allow_guest_search": settings.get("allow_guest_search", True),
            "show_generation_numbers": settings.get("show_generation_numbers", True),
            "show_birth_dates": settings.get("show_birth_dates", True),
            "show_death_dates": settings.get("show_death_dates", True),
            "show_contact_info": settings.get("show_contact_info", False),
        },
    }


@router.put("/privacy", response_model=dict)
async def update_privacy_settings(
    data: PrivacySettingsUpdate,
    request: Request,
    db: AsyncSession = Depends(get_tenant_db),
):
    """Update privacy settings"""
    tenant = require_tenant(request)
    settings = tenant.settings or {}
    
    settings["visibility_default"] = data.visibility_default
    settings["allow_guest_search"] = data.allow_guest_search
    settings["show_generation_numbers"] = data.show_generation_numbers
    settings["show_birth_dates"] = data.show_birth_dates
    settings["show_death_dates"] = data.show_death_dates
    settings["show_contact_info"] = data.show_contact_info
    
    tenant.settings = settings
    await db.commit()
    
    return {
        "success": True,
        "message": "隐私设置已更新",
    }


@router.get("/display", response_model=dict)
async def get_display_settings(
    request: Request,
    db: AsyncSession = Depends(get_tenant_db),
):
    """Get display settings"""
    tenant = require_tenant(request)
    settings = tenant.settings or {}
    
    return {
        "success": True,
        "data": {
            "theme": settings.get("theme", "light"),
            "language": settings.get("language", "zh-CN"),
            "date_format": settings.get("date_format", "YYYY-MM-DD"),
            "tree_direction": settings.get("tree_direction", "vertical"),
            "show_photos": settings.get("show_photos", True),
            "show_dates": settings.get("show_dates", True),
        },
    }


@router.put("/display", response_model=dict)
async def update_display_settings(
    data: DisplaySettingsUpdate,
    request: Request,
    db: AsyncSession = Depends(get_tenant_db),
):
    """Update display settings"""
    tenant = require_tenant(request)
    settings = tenant.settings or {}
    
    settings["theme"] = data.theme
    settings["language"] = data.language
    settings["date_format"] = data.date_format
    settings["tree_direction"] = data.tree_direction
    settings["show_photos"] = data.show_photos
    settings["show_dates"] = data.show_dates
    
    tenant.settings = settings
    await db.commit()
    
    return {
        "success": True,
        "message": "显示设置已更新",
    }