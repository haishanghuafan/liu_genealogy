"""
Subscription plans configuration
Editable for pricing adjustments
"""
from typing import Dict, Any
from pydantic import BaseModel
import json
import os

PLAN_CONFIG_FILE = os.path.join(os.path.dirname(__file__), "plans_config.json")


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


DEFAULT_SUBSCRIPTION_PLANS: Dict[str, Dict] = {
    "free": {
        "name": "免费版",
        "price_cny": 0,
        "price_usd": 0,
        "billing_period": None,
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
        "billing_period": "yearly",
        "features": PlanFeatures(
            max_persons=500,
            max_members=20,
            max_storage_mb=1024,
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
            max_storage_mb=10240,
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
            max_persons=-1,
            max_members=-1,
            max_storage_mb=102400,
            max_admins=-1,
            advanced_visualization=True,
            data_export=True,
            api_access=True,
            custom_domain=True,
            priority_support="dedicated",
        ),
    },
}

SUBSCRIPTION_PLANS: Dict[str, Dict] = {}


def _load_plans():
    """Load plans from config file or use defaults"""
    global SUBSCRIPTION_PLANS
    if os.path.exists(PLAN_CONFIG_FILE):
        try:
            with open(PLAN_CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            for plan_id, plan_data in data.items():
                features = PlanFeatures(**plan_data["features"])
                SUBSCRIPTION_PLANS[plan_id] = {
                    "name": plan_data["name"],
                    "price_cny": plan_data["price_cny"],
                    "price_usd": plan_data["price_usd"],
                    "billing_period": plan_data.get("billing_period"),
                    "features": features,
                }
        except Exception:
            SUBSCRIPTION_PLANS = DEFAULT_SUBSCRIPTION_PLANS.copy()
    else:
        SUBSCRIPTION_PLANS = DEFAULT_SUBSCRIPTION_PLANS.copy()


def _save_plans():
    """Save plans to config file"""
    data = {}
    for plan_id, plan_data in SUBSCRIPTION_PLANS.items():
        data[plan_id] = {
            "name": plan_data["name"],
            "price_cny": plan_data["price_cny"],
            "price_usd": plan_data["price_usd"],
            "billing_period": plan_data.get("billing_period"),
            "features": plan_data["features"].model_dump(),
        }
    with open(PLAN_CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


_load_plans()


def get_plan(plan_name: str) -> Dict:
    """Get plan configuration by name"""
    return SUBSCRIPTION_PLANS.get(plan_name, SUBSCRIPTION_PLANS["free"])


def get_all_plans() -> Dict:
    """Get all available plans"""
    return SUBSCRIPTION_PLANS


def update_plan(plan_id: str, updates: Dict[str, Any]) -> Dict:
    """Update plan configuration"""
    if plan_id not in SUBSCRIPTION_PLANS:
        return {}
    
    plan = SUBSCRIPTION_PLANS[plan_id]
    
    if "name" in updates:
        plan["name"] = updates["name"]
    if "price_cny" in updates:
        plan["price_cny"] = updates["price_cny"]
    if "price_usd" in updates:
        plan["price_usd"] = updates["price_usd"]
    if "billing_period" in updates:
        plan["billing_period"] = updates["billing_period"]
    if "features" in updates:
        plan["features"] = PlanFeatures(**updates["features"])
    
    _save_plans()
    return plan


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
