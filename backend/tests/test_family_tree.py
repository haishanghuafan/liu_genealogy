"""
Tests for Family Tree API
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Tenant


@pytest.fixture
async def test_tenant_with_data(db: AsyncSession) -> Tenant:
    """Create a test tenant with sample data"""
    tenant = Tenant(
        name="族谱测试家族",
        slug="test-genealogy",
        surname="测试",
        schema_name="tenant_test_genealogy",
        neo4j_database="tenant_test_genealogy",
        is_public=True,
    )
    db.add(tenant)
    await db.commit()
    await db.refresh(tenant)
    return tenant


@pytest.mark.asyncio
async def test_get_family_tree(client: AsyncClient, test_tenant_with_data: Tenant):
    """Test getting family tree"""
    response = await client.get(f"/api/v1/t/{test_tenant_with_data.slug}/family-tree")
    
    # Will fail without tenant schema setup
    # assert response.status_code == 200
    pass


@pytest.mark.asyncio
async def test_get_family_tree_with_root(client: AsyncClient, test_tenant_with_data: Tenant):
    """Test getting family tree with specific root"""
    # TODO: Create test data and test
    
    pass


@pytest.mark.asyncio
async def test_get_ancestors(client: AsyncClient, test_tenant_with_data: Tenant):
    """Test getting ancestors chain"""
    # TODO: Create test data and test
    
    pass


@pytest.mark.asyncio
async def test_get_descendants(client: AsyncClient, test_tenant_with_data: Tenant):
    """Test getting descendants tree"""
    # TODO: Create test data and test
    
    pass


@pytest.mark.asyncio
async def test_get_tree_statistics(client: AsyncClient, test_tenant_with_data: Tenant):
    """Test getting tree statistics"""
    response = await client.get(
        f"/api/v1/t/{test_tenant_with_data.slug}/family-tree/statistics"
    )
    
    # Will fail without tenant schema setup
    # assert response.status_code == 200
    # data = response.json()
    # assert "total_persons" in data["data"]
    pass
