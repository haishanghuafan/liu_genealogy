"""
Subscription plans configuration
Editable for pricing adjustments
"""
from typing import Dict
from pydantic import BaseModel


class PlanFeatures(BaseModel):
    """Features available in each plan"""
    max_persons: int
    max_members: int
    max_storage_mb: int
    max_admins: int
    advanced_visualization: bool
    data_export: bool
    api_access: bool
    custom_domain: bool
    priority_support: str  # "community" | "email" | "priority" | "dedicated"


# Subscription Plans Configuration
# Edit these values to adjust pricing and features
SUBSCRIPTION_PLANS: Dict[str, Dict] = {
    "free": {
        "name": "免费版",
        "price_cny": 0,
        "price_usd": 0,
        "billing_period": None,  # None = free forever
        "features": PlanFeatures(
            max_persons=100,
            max_members=5,
            max_storage_mb=100,
            max_admins=1,
            advanced_visualization=False,
            data_export=False,
            api_access=False,
            custom_domain=False,
            priority_support="community",
        ),
    },
    "basic": {
        "name": "基础版",
        "price_cny": 99,
        "price_usd": 14,
        "billing_period": "yearly",  # yearly | monthly
        "features": PlanFeatures(
            max_persons=500,
            max_members=20,
            max_storage_mb=1024,  # 1GB
            max_admins=3,
            advanced_visualization=True,
            data_export=True,
            api_access=False,
            custom_domain=False,
            priority_support="email",
        ),
    },
    "professional": {
        "name": "专业版",
        "price_cny": 299,
        "price_usd": 42,
        "billing_period": "yearly",
        "features": PlanFeatures(
            max_persons=5000,
            max_members=100,
            max_storage_mb=10240,  # 10GB
            max_admins=10,
            advanced_visualization=True,
            data_export=True,
            api_access=True,
            custom_domain=False,
            priority_support="priority",
        ),
    },
    "enterprise": {
        "name": "企业版",
        "price_cny": 999,
        "price_usd": 140,
        "billing_period": "yearly",
        "features": PlanFeatures(
            max_persons=-1,  # -1 = unlimited
            max_members=-1,
            max_storage_mb=102400,  # 100GB
            max_admins=-1,
            advanced_visualization=True,
            data_export=True,
            api_access=True,
            custom_domain=True,
            priority_support="dedicated",
        ),
    },
}


def get_plan(plan_name: str) -> Dict:
    """Get plan configuration by name"""
    return SUBSCRIPTION_PLANS.get(plan_name, SUBSCRIPTION_PLANS["free"])


def get_all_plans() -> Dict:
    """Get all available plans"""
    return SUBSCRIPTION_PLANS


def get_plan_features(plan_name: str) -> PlanFeatures:
    """Get features for a specific plan"""
    plan = get_plan(plan_name)
    return plan["features"]


def check_plan_limit(plan_name: str, resource: str, current_value: int) -> bool:
    """
    Check if current value exceeds plan limit
    Returns True if within limit, False if exceeded
    """
    features = get_plan_features(plan_name)
    limit = getattr(features, resource, None)
    
    # -1 means unlimited
    if limit == -1:
        return True
    
    return current_value < limit if limit else True


def format_plan_price(plan_name: str, currency: str = "CNY") -> str:
    """Format plan price for display"""
    plan = get_plan(plan_name)
    price = plan.get(f"price_{currency.lower()}", 0)
    
    if price == 0:
        return "免费"
    
    billing = plan.get("billing_period", "yearly")
    if billing == "yearly":
        return f"¥{price}/年"
    elif billing == "monthly":
        return f"¥{price}/月"
    return f"¥{price}"
