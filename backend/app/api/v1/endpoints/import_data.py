"""
Excel data import API endpoints
"""
from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_tenant_db
from app.middleware.tenant import require_tenant
from app.services.excel_import_service import ExcelImportService

router = APIRouter(prefix="/import", tags=["Data Import"])


@router.post("/excel", response_model=dict)
async def import_excel(
    file: UploadFile = File(..., description="Excel file to import"),
    request: Request = None,
    db: AsyncSession = Depends(get_tenant_db),
):
    """
    Import genealogy data from Excel file
    
    Required columns:
    - name: 姓名
    - gender: 性别 (M/F)
    
    Optional columns:
    - generation_number: 世代编号
    - branch_name: 支系名称
    - father_name: 父亲姓名
    - mother_name: 母亲姓名
    - courtesy_name: 字
    - art_name: 号
    - birth_year: 出生年份
    - death_year: 逝世年份
    - birth_place: 出生地
    - biography: 生平简介
    - sort_order: 排序
    
    Returns detailed import results with success/error for each row
    """
    tenant = require_tenant(request)
    
    # Validate file type
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(400, "只支持 Excel 文件 (.xlsx, .xls)")
    
    # Read file content
    try:
        content = await file.read()
    except Exception as e:
        raise HTTPException(400, f"文件读取失败：{str(e)}")
    
    # Import data
    service = ExcelImportService(db, tenant.slug)
    result = await service.import_from_excel(content)
    
    if result.get("success"):
        return {
            "success": True,
            "message": f"成功导入 {result.get('imported_count', 0)} 条记录",
            "imported_count": result.get('imported_count', 0),
            "error_count": result.get('error_count', 0),
            "details": result.get('details', [])
        }
    else:
        if "error" in result and len(result.get("errors", [])) == 0:
            # Global error
            raise HTTPException(400, result.get("error"))
        else:
            # Partial success
            return {
                "success": False,
                "message": f"导入完成，{result.get('imported_count', 0)} 条成功，{result.get('error_count', 0)} 条失败",
                "imported_count": result.get('imported_count', 0),
                "error_count": result.get('error_count', 0),
                "errors": result.get('errors', []),
                "details": result.get('details', [])
            }


@router.post("/excel/replace", response_model=dict)
async def replace_import_excel(
    file: UploadFile = File(..., description="Excel file to import (will replace all existing data)"),
    request: Request = None,
    db: AsyncSession = Depends(get_tenant_db),
):
    """
    Replace all existing genealogy data with new import
    
    WARNING: This will delete ALL existing persons, spouse relations, branches, and generations!
    
    Required columns:
    - name: 姓名
    - gender: 性别 (M/F)
    
    Optional columns:
    - generation_number: 世代编号
    - branch_name: 支系名称
    - father_name: 父亲姓名
    - mother_name: 母亲姓名
    - courtesy_name: 字
    - art_name: 号
    - birth_year: 出生年份
    - death_year: 逝世年份
    - birth_place: 出生地
    - biography: 生平简介
    - sort_order: 排序
    
    Returns detailed import results with success/error for each row
    """
    tenant = require_tenant(request)
    
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(400, "只支持 Excel 文件 (.xlsx, .xls)")
    
    try:
        content = await file.read()
    except Exception as e:
        raise HTTPException(400, f"文件读取失败：{str(e)}")
    
    service = ExcelImportService(db, tenant.slug)
    result = await service.replace_import(content)
    
    if result.get("success"):
        return {
            "success": True,
            "message": f"已替换所有数据，成功导入 {result.get('imported_count', 0)} 条记录",
            "imported_count": result.get('imported_count', 0),
            "error_count": result.get('error_count', 0),
            "details": result.get('details', [])
        }
    else:
        if "error" in result and len(result.get("errors", [])) == 0:
            raise HTTPException(400, result.get("error"))
        else:
            return {
                "success": False,
                "message": f"导入完成，{result.get('imported_count', 0)} 条成功，{result.get('error_count', 0)} 条失败",
                "imported_count": result.get('imported_count', 0),
                "error_count": result.get('error_count', 0),
                "errors": result.get('errors', []),
                "details": result.get('details', [])
            }


@router.get("/excel-template", response_model=dict)
async def get_excel_template():
    """
    Get Excel import template structure
    
    Returns column names and descriptions for creating import files
    """
    return {
        "success": True,
        "template": {
            "required_columns": [
                {"name": "name", "description": "姓名", "type": "string"},
                {"name": "gender", "description": "性别 (M=男，F=女)", "type": "string"}
            ],
            "optional_columns": [
                {"name": "generation_number", "description": "世代编号", "type": "integer"},
                {"name": "branch_name", "description": "支系名称", "type": "string"},
                {"name": "father_name", "description": "父亲姓名", "type": "string"},
                {"name": "mother_name", "description": "母亲姓名", "type": "string"},
                {"name": "courtesy_name", "description": "字", "type": "string"},
                {"name": "art_name", "description": "号", "type": "string"},
                {"name": "birth_year", "description": "出生年份", "type": "integer"},
                {"name": "death_year", "description": "逝世年份", "type": "integer"},
                {"name": "birth_place", "description": "出生地", "type": "string"},
                {"name": "biography", "description": "生平简介", "type": "string"},
                {"name": "sort_order", "description": "排序", "type": "integer"}
            ],
            "example_data": [
                {
                    "name": "刘邦",
                    "gender": "M",
                    "generation_number": 1,
                    "branch_name": "沛县支系",
                    "birth_year": -256,
                    "death_year": -195
                },
                {
                    "name": "刘盈",
                    "gender": "M",
                    "generation_number": 2,
                    "father_name": "刘邦",
                    "birth_year": -210,
                    "death_year": -188
                }
            ]
        }
    }
