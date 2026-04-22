"""
Subscription management endpoints

Public:  /api/v1/subscription/plans          (list plans)
Tenant:  /api/v1/t/{tenant_slug}/subscription/* (manage subscription)
"""
from datetime import datetime, timezone, timedelta
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel, Field
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.plans import get_plan, get_all_plans, format_plan_price, update_plan
from app.middleware.tenant import require_tenant
from app.middleware.auth import get_superuser
from app.models.system import Subscription, Tenant, TenantUser

router = APIRouter(prefix="/subscription", tags=["Subscription"])

# Tenant-specific sub-router
tenant_subscription_router = APIRouter(prefix="/subscription", tags=["Subscription"])


# ============ Schemas ============

class SubscriptionUpgrade(BaseModel):
    new_plan: str = Field(..., pattern="^(basic|professional|enterprise)$")


class SubscriptionCreate(BaseModel):
    plan: str = Field(..., pattern="^(free|basic|professional|enterprise)$")
    payment_method: str = "manual"


class PlanUpdate(BaseModel):
    name: Optional[str] = None
    price_cny: Optional[float] = None
    price_usd: Optional[float] = None
    billing_period: Optional[str] = None
    features: Optional[dict] = None


# ============ Admin Endpoints ============

@router.get("/admin/plans", response_model=dict)
async def admin_list_plans(
    _admin=Depends(get_superuser),
):
    """Admin: List all subscription plans with full details"""
    plans = get_all_plans()
    result = []
    for plan_id, plan_data in plans.items():
        result.append({
            "id": plan_id,
            "name": plan_data["name"],
            "price_cny": plan_data["price_cny"],
            "price_usd": plan_data["price_usd"],
            "billing_period": plan_data.get("billing_period"),
            "features": {
                "max_persons": plan_data["features"].max_persons,
                "max_members": plan_data["features"].max_members,
                "max_storage_mb": plan_data["features"].max_storage_mb,
                "max_admins": plan_data["features"].max_admins,
                "advanced_visualization": plan_data["features"].advanced_visualization,
                "data_export": plan_data["features"].data_export,
                "api_access": plan_data["features"].api_access,
                "custom_domain": plan_data["features"].custom_domain,
                "priority_support": plan_data["features"].priority_support,
            },
        })
    
    return {"success": True, "data": result}


@router.put("/admin/plans/{plan_id}", response_model=dict)
async def admin_update_plan(
    plan_id: str,
    data: PlanUpdate,
    _admin=Depends(get_superuser),
):
    """Admin: Update a subscription plan configuration"""
    updates = data.model_dump(exclude_unset=True)
    updated_plan = update_plan(plan_id, updates)
    
    if not updated_plan:
        raise HTTPException(404, f"Plan '{plan_id}' not found")
    
    return {
        "success": True,
        "message": f"套餐 '{updated_plan['name']}' 已更新",
        "data": {
            "id": plan_id,
            "name": updated_plan["name"],
            "price_cny": updated_plan["price_cny"],
            "price_usd": updated_plan["price_usd"],
            "billing_period": updated_plan.get("billing_period"),
            "features": {
                "max_persons": updated_plan["features"].max_persons,
                "max_members": updated_plan["features"].max_members,
                "max_storage_mb": updated_plan["features"].max_storage_mb,
                "max_admins": updated_plan["features"].max_admins,
                "advanced_visualization": updated_plan["features"].advanced_visualization,
                "data_export": updated_plan["features"].data_export,
                "api_access": updated_plan["features"].api_access,
                "custom_domain": updated_plan["features"].custom_domain,
                "priority_support": updated_plan["features"].priority_support,
            },
        },
    }


# ============ Public Endpoints ============

@router.get("/plans", response_model=dict)
async def list_plans(
    currency: str = Query("CNY", pattern="^(CNY|USD)$"),
):
    """List all available subscription plans with features and pricing"""
    plans = get_all_plans()
    
    result = []
    for plan_id, plan_data in plans.items():
        result.append({
            "id": plan_id,
            "name": plan_data["name"],
            "price": plan_data[f"price_{currency.lower()}"],
            "price_display": format_plan_price(plan_id, currency),
            "billing_period": plan_data.get("billing_period"),
            "features": {
                "max_persons": plan_data["features"].max_persons,
                "max_members": plan_data["features"].max_members,
                "max_storage_mb": plan_data["features"].max_storage_mb,
                "max_admins": plan_data["features"].max_admins,
                "advanced_visualization": plan_data["features"].advanced_visualization,
                "data_export": plan_data["features"].data_export,
                "api_access": plan_data["features"].api_access,
                "custom_domain": plan_data["features"].custom_domain,
                "priority_support": plan_data["features"].priority_support,
            },
        })
    
    return {"success": True, "data": result}


# ============ Tenant-scoped Endpoints ============

@tenant_subscription_router.get("/current", response_model=dict)
async def get_current_subscription(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Get current subscription status for tenant"""
    tenant = require_tenant(request)
    
    stmt = select(Subscription).where(
        and_(
            Subscription.tenant_id == tenant.id,
            Subscription.status == "active",
            Subscription.expires_at > datetime.now(timezone.utc),
        )
    )
    result = await db.execute(stmt)
    subscription = result.scalar_one_or_none()
    
    plan_info = get_plan(tenant.plan)
    
    return {
        "success": True,
        "data": {
            "tenant_id": str(tenant.id),
            "current_plan": tenant.plan,
            "plan_name": plan_info["name"],
            "subscription": {
                "id": str(subscription.id) if subscription else None,
                "plan": subscription.plan if subscription else tenant.plan,
                "started_at": subscription.started_at.isoformat() if subscription else None,
                "expires_at": subscription.expires_at.isoformat() if subscription else None,
                "status": subscription.status if subscription else "active",
            } if subscription else None,
        },
    }


@tenant_subscription_router.get("/quotas", response_model=dict)
async def get_quota_status(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Get current resource usage and limits"""
    tenant = require_tenant(request)
    from app.services.quota_service import quota_service
    
    # Count members
    members_stmt = select(func.count()).select_from(TenantUser).where(
        TenantUser.tenant_id == tenant.id
    )
    members_count = (await db.execute(members_stmt)).scalar() or 0
    
    # Count admins
    admins_stmt = select(func.count()).select_from(TenantUser).where(
        and_(TenantUser.tenant_id == tenant.id, TenantUser.role == "tenant_admin")
    )
    admins_count = (await db.execute(admins_stmt)).scalar() or 0
    
    quotas = await quota_service.get_all_quotas(
        plan=tenant.plan,
        db=db,
        current_members=members_count,
        current_admins=admins_count,
    )
    
    return quotas


@tenant_subscription_router.post("/upgrade", response_model=dict)
async def upgrade_subscription(
    data: SubscriptionUpgrade,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Upgrade subscription plan"""
    tenant = require_tenant(request)
    
    new_plan_info = get_plan(data.new_plan)
    if not new_plan_info:
        raise HTTPException(400, "Invalid plan")
    
    stmt = select(Subscription).where(
        and_(Subscription.tenant_id == tenant.id, Subscription.status == "active")
    )
    result = await db.execute(stmt)
    subscription = result.scalar_one_or_none()
    
    if subscription and subscription.expires_at > datetime.now(timezone.utc):
        new_expires = subscription.expires_at + timedelta(days=365)
    else:
        new_expires = datetime.now(timezone.utc) + timedelta(days=365)
    
    if subscription:
        subscription.plan = data.new_plan
        subscription.amount = new_plan_info["price_cny"]
        subscription.expires_at = new_expires
        subscription.status = "active"
    else:
        subscription = Subscription(
            tenant_id=tenant.id,
            plan=data.new_plan,
            amount=new_plan_info["price_cny"],
            started_at=datetime.now(timezone.utc),
            expires_at=new_expires,
            status="active",
        )
        db.add(subscription)
    
    tenant.plan = data.new_plan
    tenant.max_persons = new_plan_info["features"].max_persons if new_plan_info["features"].max_persons != -1 else 999999
    tenant.max_members = new_plan_info["features"].max_members if new_plan_info["features"].max_members != -1 else 999999
    tenant.max_storage_mb = new_plan_info["features"].max_storage_mb if new_plan_info["features"].max_storage_mb != -1 else 999999
    
    await db.commit()
    
    return {
        "success": True,
        "message": f"已成功升级到 {new_plan_info['name']}",
        "data": {"plan": data.new_plan, "plan_name": new_plan_info["name"], "expires_at": new_expires.isoformat()},
    }


@tenant_subscription_router.post("/cancel", response_model=dict)
async def cancel_subscription(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Cancel subscription, revert to free plan"""
    tenant = require_tenant(request)
    
    if tenant.plan == "free":
        raise HTTPException(400, "Already on free plan")
    
    stmt = select(Subscription).where(
        and_(Subscription.tenant_id == tenant.id, Subscription.status == "active")
    )
    result = await db.execute(stmt)
    subscription = result.scalar_one_or_none()
    
    if subscription:
        subscription.status = "cancelled"
        subscription.expires_at = datetime.now(timezone.utc)
    
    tenant.plan = "free"
    tenant.max_persons = 100
    tenant.max_members = 5
    tenant.max_storage_mb = 100
    
    await db.commit()
    
    return {"success": True, "message": "订阅已取消，已降级为免费版"}


@tenant_subscription_router.post("/create-free", response_model=dict)
async def create_free_subscription(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Activate free subscription for tenant"""
    tenant = require_tenant(request)
    
    stmt = select(Subscription).where(Subscription.tenant_id == tenant.id)
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise HTTPException(400, "Subscription already exists")
    
    subscription = Subscription(
        tenant_id=tenant.id,
        plan="free",
        amount=0,
        started_at=datetime.now(timezone.utc),
        expires_at=datetime.now(timezone.utc) + timedelta(days=365 * 10),
        status="active",
    )
    db.add(subscription)
    await db.commit()
    
    return {"success": True, "message": "免费套餐已激活", "data": {"plan": "free", "expires_at": subscription.expires_at.isoformat()}}
