"""
Tenant middleware for multi-tenant request handling
"""
import re
from typing import Optional

from fastapi import HTTPException, Request, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.core.database import tenant_session
from app.models.system import Tenant


class TenantMiddleware(BaseHTTPMiddleware):
    """
    Middleware to identify and set tenant context for each request.
    
    Tenant identification order:
    1. Subdomain (e.g., liu.genealogy.com)
    2. URL path (e.g., /t/liu/...)
    3. Header (X-Tenant-ID)
    """
    
    # Paths that don't require tenant context
    PUBLIC_PATHS = [
        "/api/v1/auth",
        "/api/v1/tenants",
        "/api/v1/admin",
        "/docs",
        "/openapi",
        "/health",
        "/",
    ]
    
    # Path prefix for tenant-specific routes
    TENANT_PATH_PREFIX = "/t/"
    
    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        
        if self._is_public_path(path):
            request.state.tenant = None
            return await call_next(request)
        
        tenant_slug = await self._extract_tenant_slug(request)
        
        if tenant_slug:
            # Load tenant from database
            tenant = await self._get_tenant(request, tenant_slug)
            
            if tenant is None:
                return JSONResponse(
                    status_code=status.HTTP_404_NOT_FOUND,
                    content={
                        "success": False,
                        "error": {
                            "code": "TENANT_NOT_FOUND",
                            "message": f"Tenant '{tenant_slug}' not found",
                        },
                    },
                )
            
            if not tenant.is_active:
                return JSONResponse(
                    status_code=status.HTTP_403_FORBIDDEN,
                    content={
                        "success": False,
                        "error": {
                            "code": "TENANT_INACTIVE",
                            "message": "This family site is currently inactive",
                        },
                    },
                )
            
            # Set tenant context
            request.state.tenant = tenant
            request.state.tenant_schema = tenant.schema_name
            request.state.tenant_neo4j = tenant.neo4j_database
        else:
            # No tenant identified
            request.state.tenant = None
        
        return await call_next(request)
    
    def _is_public_path(self, path: str) -> bool:
        """Check if path is public (doesn't require tenant)"""
        if path.startswith("/api/v1/t/"):
            return False
        for public_path in self.PUBLIC_PATHS:
            if path.startswith(public_path) or path == public_path:
                return True
        return False
    
    async def _extract_tenant_slug(self, request: Request) -> Optional[str]:
        """Extract tenant slug from request"""
        path = request.url.path
        
        match = re.search(r'(?:/api/v1)?/t/([^/]+)', path)
        if match:
            return match.group(1)
        
        # Method 2: Subdomain (tenant.genealogy.com)
        host = request.headers.get("host", "")
        if host and "." in host:
            subdomain = host.split(".")[0]
            # Skip common subdomains
            if subdomain not in ("www", "api", "admin", "app"):
                return subdomain
        
        # Method 3: Header (X-Tenant-ID)
        tenant_header = request.headers.get("X-Tenant-ID")
        if tenant_header:
            return tenant_header
        
        return None
    
    async def _get_tenant(self, request: Request, slug: str) -> Optional[Tenant]:
        """Load tenant from database"""
        from sqlalchemy import select
        from app.core.database import db_manager
        
        session_maker = db_manager.get_session_maker("public")
        async with session_maker() as session:
            stmt = select(Tenant).where(Tenant.slug == slug)
            result = await session.execute(stmt)
            return result.scalar_one_or_none()


def get_tenant(request: Request) -> Optional[Tenant]:
    """Get current tenant from request state"""
    return getattr(request.state, "tenant", None)


def require_tenant(request: Request) -> Tenant:
    """Get current tenant or raise 404"""
    tenant = get_tenant(request)
    if tenant is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found",
        )
    return tenant
