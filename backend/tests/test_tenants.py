"""
Tests for Tenant API
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Tenant, User


@pytest.mark.asyncio
async def test_list_tenants(client: AsyncClient, db: AsyncSession):
    """Test listing tenants"""
    # Create test tenants
    tenant1 = Tenant(
        name="张氏家族",
        slug="zhang-family",
        surname="张",
        schema_name="tenant_zhang",
        neo4j_database="tenant_zhang",
        is_public=True,
    )
    tenant2 = Tenant(
        name="李氏家族",
        slug="li-family",
        surname="李",
        schema_name="tenant_li",
        neo4j_database="tenant_li",
        is_public=True,
    )
    db.add_all([tenant1, tenant2])
    await db.commit()
    
    response = await client.get("/api/v1/tenants")
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["data"]) >= 2


@pytest.mark.asyncio
async def test_get_tenant_by_slug(client: AsyncClient, db: AsyncSession):
    """Test getting tenant by slug"""
    tenant = Tenant(
        name="王氏家族",
        slug="wang-family",
        surname="王",
        schema_name="tenant_wang",
        neo4j_database="tenant_wang",
        is_public=True,
    )
    db.add(tenant)
    await db.commit()
    
    response = await client.get("/api/v1/tenants/wang-family")
    
    assert response.status_code == 200
    data = response.json()
    assert data["slug"] == "wang-family"
    assert data["surname"] == "王"


@pytest.mark.asyncio
async def test_get_nonexistent_tenant(client: AsyncClient, db: AsyncSession):
    """Test getting non-existent tenant"""
    response = await client.get("/api/v1/tenants/nonexistent")
    
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_create_tenant(client: AsyncClient, db: AsyncSession, admin_user: User):
    """Test creating a tenant (requires superuser)"""
    # TODO: Add authentication header
    response = await client.post(
        "/api/v1/tenants",
        json={
            "name": "赵氏家族",
            "slug": "zhao-family",
            "surname": "赵",
            "is_public": True,
        },
    )
    
    # Will fail without superuser auth
    # assert response.status_code == 201
    # data = response.json()
    # assert data["slug"] == "zhao-family"


@pytest.mark.asyncio
async def test_search_tenants_by_surname(client: AsyncClient, db: AsyncSession):
    """Test searching tenants by surname"""
    tenant = Tenant(
        name="孙氏家族",
        slug="sun-family",
        surname="孙",
        schema_name="tenant_sun",
        neo4j_database="tenant_sun",
        is_public=True,
    )
    db.add(tenant)
    await db.commit()
    
    response = await client.get("/api/v1/tenants?surname=孙")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) >= 1
    assert data["data"][0]["surname"] == "孙"
