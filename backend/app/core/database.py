"""
Database configuration and session management
"""
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Optional

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings


class Base(DeclarativeBase):
    """Base class for all models"""
    pass


class DatabaseManager:
    """Database manager for multi-tenant support"""
    
    def __init__(self):
        self._engines: dict[str, AsyncEngine] = {}
        self._session_makers: dict[str, async_sessionmaker[AsyncSession]] = {}
        self._default_engine: Optional[AsyncEngine] = None
        self._default_session_maker: Optional[async_sessionmaker[AsyncSession]] = None
    
    def init_default_engine(self) -> None:
        """Initialize default engine for system database"""
        # SQLite doesn't support pool_size
        db_url = str(settings.database_url)
        if db_url.startswith("sqlite"):
            self._default_engine = create_async_engine(
                db_url,
                echo=settings.debug,
                future=True,
            )
        else:
            self._default_engine = create_async_engine(
                db_url,
                pool_size=settings.database_pool_size,
                max_overflow=settings.database_max_overflow,
                echo=settings.debug,
            )
        self._default_session_maker = async_sessionmaker(
            bind=self._default_engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )
    
    def get_engine(self, schema_name: str = "public") -> AsyncEngine:
        """Get or create engine for a specific schema"""
        if schema_name == "public" and self._default_engine:
            return self._default_engine
        
        if schema_name not in self._engines:
            # SQLite doesn't support schema-based multi-tenancy
            # Use separate database files instead
            db_url = str(settings.database_url)
            if db_url.startswith("sqlite"):
                # Each tenant gets its own SQLite file
                import os
                db_dir = os.path.join(os.path.dirname(db_url.replace("sqlite+aiosqlite:///", "")), "tenants")
                os.makedirs(db_dir, exist_ok=True)
                db_url = f"sqlite+aiosqlite:///{db_dir}/{schema_name}.db"
                engine = create_async_engine(
                    db_url,
                    echo=settings.debug,
                    future=True,
                )
            else:
                # PostgreSQL: use schema-based multi-tenancy
                engine = create_async_engine(
                    db_url,
                    pool_size=5,
                    max_overflow=5,
                    echo=settings.debug,
                    connect_args={"server_side_cursors": True},
                )
            self._engines[schema_name] = engine
            self._session_makers[schema_name] = async_sessionmaker(
                bind=engine,
                class_=AsyncSession,
                expire_on_commit=False,
                autocommit=False,
                autoflush=False,
            )
        
        return self._engines[schema_name]
    
    def get_session_maker(self, schema_name: str = "public") -> async_sessionmaker[AsyncSession]:
        """Get session maker for a specific schema"""
        if schema_name == "public" and self._default_session_maker:
            return self._default_session_maker
        
        if schema_name not in self._session_makers:
            self.get_engine(schema_name)
        
        return self._session_makers[schema_name]
    
    async def close(self) -> None:
        """Close all database connections"""
        if self._default_engine:
            await self._default_engine.dispose()
        
        for engine in self._engines.values():
            await engine.dispose()
        
        self._engines.clear()
        self._session_makers.clear()


# Global database manager instance
db_manager = DatabaseManager()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting database session"""
    session_maker = db_manager.get_session_maker("public")
    async with session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def get_tenant_db(schema_name: str) -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting tenant-specific database session"""
    # Skip SET search_path for SQLite
    db_url = str(settings.database_url)
    is_sqlite = db_url.startswith("sqlite")
    
    session_maker = db_manager.get_session_maker(schema_name)
    async with session_maker() as session:
        try:
            if not is_sqlite:
                await session.execute(f"SET search_path TO {schema_name}")
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


@asynccontextmanager
async def tenant_session(schema_name: str) -> AsyncGenerator[AsyncSession, None]:
    """Context manager for tenant-specific database session"""
    # Skip SET search_path for SQLite
    db_url = str(settings.database_url)
    is_sqlite = db_url.startswith("sqlite")
    
    session_maker = db_manager.get_session_maker(schema_name)
    async with session_maker() as session:
        try:
            if not is_sqlite:
                await session.execute(f"SET search_path TO {schema_name}")
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
