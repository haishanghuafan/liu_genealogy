"""
API v1 router configuration
"""
from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth, 
    tenants, 
    family_tree, 
    persons, 
    subscriptions, 
    members,
    settings,
    files,
    search,
    analytics_endpoints as analytics,
    records,
    export,
    branches,
    generations,
    spouse_relations,
    import_data,
)

api_router = APIRouter()

# Include system-level endpoint routers (public)
api_router.include_router(auth.router)
api_router.include_router(tenants.router)

# Subscription plans (public)
api_router.include_router(subscriptions.router)

# Tenant-specific routers (under /t/{tenant_slug})
tenant_router = APIRouter(prefix="/t/{tenant_slug}")
tenant_router.include_router(persons.router)
tenant_router.include_router(family_tree.router)
tenant_router.include_router(members.router)
tenant_router.include_router(subscriptions.tenant_subscription_router)
tenant_router.include_router(settings.router)
tenant_router.include_router(files.router)
tenant_router.include_router(search.router)
tenant_router.include_router(analytics.router)
tenant_router.include_router(records.router)
tenant_router.include_router(export.router)
tenant_router.include_router(branches.router)
tenant_router.include_router(generations.router)
tenant_router.include_router(spouse_relations.router)
tenant_router.include_router(import_data.router)

api_router.include_router(tenant_router)