"""
Resource quota service - checks tenant plan limits
"""
from dataclasses import dataclass
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.plans import get_plan_features, check_plan_limit


@dataclass
class QuotaCheckResult:
    """Result of a quota check"""
    resource: str
    current: int
    limit: int  # -1 = unlimited
    allowed: bool
    plan: str


class QuotaService:
    """Service to check and enforce tenant resource quotas"""

    def __init__(self):
        self._counters_cache: dict = {}

    async def check_persons_quota(
        self,
        plan: str,
        db: AsyncSession,
        tenant_model_person,
    ) -> QuotaCheckResult:
        """Check if tenant can add more persons"""
        features = get_plan_features(plan)
        limit = features.max_persons

        from app.models.tenant import Person
        count = (await db.execute(select(func.count()).select_from(Person))).scalar() or 0

        return QuotaCheckResult(
            resource="persons",
            current=count,
            limit=limit,
            allowed=limit == -1 or count < limit,
            plan=plan,
        )

    async def check_members_quota(
        self,
        plan: str,
        current_members: int,
    ) -> QuotaCheckResult:
        """Check if tenant can add more members"""
        features = get_plan_features(plan)
        limit = features.max_members

        return QuotaCheckResult(
            resource="members",
            current=current_members,
            limit=limit,
            allowed=limit == -1 or current_members < limit,
            plan=plan,
        )

    async def check_admins_quota(
        self,
        plan: str,
        current_admins: int,
    ) -> QuotaCheckResult:
        """Check if tenant can add more admins"""
        features = get_plan_features(plan)
        limit = features.max_admins

        return QuotaCheckResult(
            resource="admins",
            current=current_admins,
            limit=limit,
            allowed=limit == -1 or current_admins < limit,
            plan=plan,
        )

    async def check_storage_quota(
        self,
        plan: str,
        current_usage_mb: float,
    ) -> QuotaCheckResult:
        """Check if tenant can upload more files"""
        features = get_plan_features(plan)
        limit = features.max_storage_mb

        return QuotaCheckResult(
            resource="storage_mb",
            current=int(current_usage_mb),
            limit=limit,
            allowed=limit == -1 or current_usage_mb < limit,
            plan=plan,
        )

    async def get_all_quotas(
        self,
        plan: str,
        db: AsyncSession,
        current_members: int,
        current_admins: int,
        current_storage_mb: float = 0.0,
    ) -> dict:
        """Get all quota statuses for a tenant"""
        features = get_plan_features(plan)

        from app.models.tenant import Person
        person_count = (await db.execute(
            select(func.count()).select_from(Person)
        )).scalar() or 0

        return {
            "plan": plan,
            "quotas": {
                "persons": {
                    "current": person_count,
                    "limit": features.max_persons,
                    "display_limit": "unlimited" if features.max_persons == -1 else str(features.max_persons),
                    "used_percent": 0 if features.max_persons == -1 else round(person_count / features.max_persons * 100, 1),
                    "allowed": features.max_persons == -1 or person_count < features.max_persons,
                },
                "members": {
                    "current": current_members,
                    "limit": features.max_members,
                    "display_limit": "unlimited" if features.max_members == -1 else str(features.max_members),
                    "used_percent": 0 if features.max_members == -1 else round(current_members / features.max_members * 100, 1),
                    "allowed": features.max_members == -1 or current_members < features.max_members,
                },
                "admins": {
                    "current": current_admins,
                    "limit": features.max_admins,
                    "display_limit": "unlimited" if features.max_admins == -1 else str(features.max_admins),
                    "used_percent": 0 if features.max_admins == -1 else round(current_admins / features.max_admins * 100, 1),
                    "allowed": features.max_admins == -1 or current_admins < features.max_admins,
                },
                "storage": {
                    "current_mb": round(current_storage_mb, 2),
                    "limit_mb": features.max_storage_mb,
                    "display_limit": "unlimited" if features.max_storage_mb == -1 else f"{features.max_storage_mb}MB",
                    "used_percent": 0 if features.max_storage_mb == -1 else round(current_storage_mb / features.max_storage_mb * 100, 1),
                    "allowed": features.max_storage_mb == -1 or current_storage_mb < features.max_storage_mb,
                },
            },
            "features": {
                "advanced_visualization": features.advanced_visualization,
                "data_export": features.data_export,
                "api_access": features.api_access,
                "custom_domain": features.custom_domain,
                "priority_support": features.priority_support,
            },
        }


def format_quota_error(result: QuotaCheckResult) -> str:
    """Format a human-readable quota error message"""
    if result.allowed:
        return ""
    
    resource_names = {
        "persons": "人物",
        "members": "成员",
        "admins": "管理员",
        "storage_mb": "存储空间",
    }
    
    limit_str = "unlimited" if result.limit == -1 else str(result.limit)
    name = resource_names.get(result.resource, result.resource)
    
    return (
        f"{name}配额已满 (当前: {result.current}/{limit_str})。"
        f"请升级套餐以获取更多资源。"
    )


quota_service = QuotaService()
