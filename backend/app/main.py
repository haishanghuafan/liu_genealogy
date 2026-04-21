"""
Genealogy SaaS - FastAPI Application Entry Point
"""
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import api_router
from app.core.config import settings
from app.core.database import db_manager
from app.core.services import connect_services, disconnect_services
from app.middleware.tenant import TenantMiddleware
from app.middleware.analytics import AnalyticsMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan events"""
    # Startup
    db_manager.init_default_engine()
    
    # Create database tables
    from app.models import Tenant, User, TenantUser, Subscription
    from app.models.tenant import Person, Generation, Branch, SpouseRelation
    from app.models.tenant import PageView, DailyVisitStats
    async with db_manager._default_engine.begin() as conn:
        from app.core.database import Base
        await conn.run_sync(Base.metadata.create_all)
    
    print(f"[START] {settings.app_name} v{settings.app_version} started")
    print(f"[INFO] Environment: {settings.environment}")
    
    # Connect to optional services (Neo4j, Redis, Meilisearch)
    # These are optional - app will still work if they're not available
    service_status = await connect_services()
    
    print("")
    print("[STATUS] Service Status:")
    print(f"   Database: [OK] SQLite/PostgreSQL")
    print(f"   Neo4j:    {'[OK] Connected' if service_status['neo4j'] else '[--] Not available (optional)'}")
    print(f"   Redis:    {'[OK] Connected' if service_status['redis'] else '[--] Not available (optional)'}")
    print(f"   Search:   {'[OK] Connected' if service_status['meilisearch'] else '[--] Not available (optional)'}")
    print("")
    
    yield
    
    # Shutdown
    await disconnect_services()
    await db_manager.close()
    print(f"[STOP] {settings.app_name} shut down")


def create_application() -> FastAPI:
    """Create FastAPI application"""
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="Multi-tenant Genealogy SaaS Platform",
        openapi_url=f"{settings.api_v1_prefix}/openapi.json",
        docs_url=f"{settings.api_v1_prefix}/docs",
        redoc_url=f"{settings.api_v1_prefix}/redoc",
        lifespan=lifespan,
    )
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Tenant middleware
    app.add_middleware(TenantMiddleware)
    
    # Analytics middleware (after tenant to have access to tenant info)
    app.add_middleware(AnalyticsMiddleware)
    
    # Include API routes
    app.include_router(api_router, prefix=settings.api_v1_prefix)
    
    # Health check endpoint
    @app.get("/health")
    async def health_check():
        from app.core.services import neo4j_service, redis_service, meilisearch_service
        
        return {
            "status": "healthy",
            "version": settings.app_version,
            "services": {
                "database": "connected",
                "neo4j": "connected" if neo4j_service.is_available else "unavailable",
                "redis": "connected" if redis_service.is_available else "unavailable",
                "search": "connected" if meilisearch_service.is_available else "unavailable",
            }
        }
    
    return app


app = create_application()


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )
