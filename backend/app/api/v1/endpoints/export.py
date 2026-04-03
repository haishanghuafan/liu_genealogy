"""
Export API endpoints - download genealogy data as Excel/PDF
"""
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_tenant_db
from app.middleware.tenant import require_tenant
from app.middleware.auth import get_current_user_required
from app.services.export_service import export_service

router = APIRouter(prefix="/export", tags=["Export"])


@router.get("/persons/excel")
async def export_persons_excel(
    request: Request,
    generation: Optional[int] = None,
    branch: Optional[str] = None,
    db: AsyncSession = Depends(get_tenant_db),
    user = Depends(get_current_user_required),
):
    """Export persons to Excel file"""
    tenant = require_tenant(request)
    
    # Check feature access
    from app.core.plans import get_plan_features
    features = get_plan_features(tenant.plan)
    
    if not features.data_export:
        raise HTTPException(403, "当前套餐不支持数据导出，请升级到专业版或更高")
    
    # Generate Excel
    excel_file = await export_service.export_persons_excel(
        db=db,
        tenant_slug=tenant.slug,
        generation_filter=generation,
        branch_filter=branch,
    )
    
    filename = f"{tenant.name}_人物列表_{datetime.now().strftime('%Y%m%d')}.xlsx"
    
    return StreamingResponse(
        excel_file,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{filename}"},
    )


@router.get("/generations/excel")
async def export_generations_excel(
    request: Request,
    db: AsyncSession = Depends(get_tenant_db),
    user = Depends(get_current_user_required),
):
    """Export generations to Excel"""
    tenant = require_tenant(request)
    
    excel_file = await export_service.export_generations_excel(db)
    
    filename = f"{tenant.name}_世代列表_{datetime.now().strftime('%Y%m%d')}.xlsx"
    
    return StreamingResponse(
        excel_file,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{filename}"},
    )


@router.get("/relations/excel")
async def export_relations_excel(
    request: Request,
    db: AsyncSession = Depends(get_tenant_db),
    user = Depends(get_current_user_required),
):
    """Export spouse relations to Excel"""
    tenant = require_tenant(request)
    
    excel_file = await export_service.export_spouse_relations_excel(db)
    
    filename = f"{tenant.name}_配偶关系_{datetime.now().strftime('%Y%m%d')}.xlsx"
    
    return StreamingResponse(
        excel_file,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{filename}"},
    )


@router.get("/full/excel")
async def export_full_excel(
    request: Request,
    db: AsyncSession = Depends(get_tenant_db),
    user = Depends(get_current_user_required),
):
    """Export full genealogy data to Excel (all sheets)"""
    tenant = require_tenant(request)
    
    # Check feature access
    from app.core.plans import get_plan_features
    features = get_plan_features(tenant.plan)
    
    if not features.data_export:
        raise HTTPException(403, "当前套餐不支持数据导出，请升级到专业版或更高")
    
    excel_file = await export_service.export_full_excel(db, tenant.slug)
    
    filename = f"{tenant.name}_族谱数据_{datetime.now().strftime('%Y%m%d')}.xlsx"
    
    return StreamingResponse(
        excel_file,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{filename}"},
    )
