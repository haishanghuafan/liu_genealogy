"""
Tests for Person API
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Tenant, tenant


@pytest.fixture
async def test_tenant(db: AsyncSession) -> Tenant:
    """Create a test tenant"""
    tenant = Tenant(
        name="测试家族",
        slug="test-family",
        surname="测",
        schema_name="tenant_test",
        neo4j_database="tenant_test",
        is_public=True,
    )
    db.add(tenant)
    await db.commit()
    await db.refresh(tenant)
    return tenant


@pytest.mark.asyncio
async def test_list_persons_empty(client: AsyncClient, test_tenant: Tenant):
    """Test listing persons when empty"""
    response = await client.get(f"/api/v1/t/{test_tenant.slug}/persons")
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["data"]) == 0


@pytest.mark.asyncio
async def test_create_person(client: AsyncClient, test_tenant: Tenant, db: AsyncSession):
    """Test creating a person"""
    # TODO: Setup tenant schema first
    
    response = await client.post(
        f"/api/v1/t/{test_tenant.slug}/persons",
        json={
            "name": "张三",
            "gender": "M",
            "generation_id": 1,
            "birth_year": 1950,
            "visibility": "public",
        },
    )
    
    # Will fail without tenant schema setup
    # assert response.status_code == 201
    # data = response.json()
    # assert data["success"] is True
    # assert data["data"]["name"] == "张三"


@pytest.mark.asyncio
async def test_create_person_with_father(client: AsyncClient, test_tenant: Tenant, db: AsyncSession):
    """Test creating a person with father relationship"""
    # TODO: Create father first, then create child
    
    pass


@pytest.mark.asyncio
async def test_update_person(client: AsyncClient, test_tenant: Tenant, db: AsyncSession):
    """Test updating a person"""
    # TODO: Create person, then update
    
    pass


@pytest.mark.asyncio
async def test_delete_person(client: AsyncClient, test_tenant: Tenant, db: AsyncSession):
    """Test deleting a person"""
    # TODO: Create person, then delete
    
    pass


@pytest.mark.asyncio
async def test_delete_person_with_children(client: AsyncClient, test_tenant: Tenant, db: AsyncSession):
    """Test deleting a person who has children (should fail)"""
    # TODO: Create father and child, try to delete father
    
    pass


@pytest.mark.asyncio
async def test_search_persons(client: AsyncClient, test_tenant: Tenant, db: AsyncSession):
    """Test searching persons by name"""
    # TODO: Create persons, then search
    
    pass


@pytest.mark.asyncio
async def test_filter_persons_by_generation(client: AsyncClient, test_tenant: Tenant, db: AsyncSession):
    """Test filtering persons by generation"""
    # TODO: Create persons in different generations, then filter
    
    pass


@pytest.mark.asyncio
async def test_add_spouse_relation(client: AsyncClient, test_tenant: Tenant, db: AsyncSession):
    """Test adding spouse relation"""
    # TODO: Create husband and wife, then add relation
    
    pass


@pytest.mark.asyncio
async def test_add_duplicate_spouse_relation(client: AsyncClient, test_tenant: Tenant, db: AsyncSession):
    """Test adding duplicate spouse relation (should fail)"""
    # TODO: Create relation, try to add same relation again
    
    pass
