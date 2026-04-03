"""
Service to sync data from PostgreSQL to Neo4j
"""
import asyncio
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tenant import Person, SpouseRelation
from app.services.neo4j_service import (
    create_father_child_relationship,
    create_person_node,
    create_spouse_relationship,
    get_neo4j_client,
)


class GraphSyncService:
    """Service to sync PostgreSQL data to Neo4j"""
    
    def __init__(self, tenant_database: str):
        self.tenant_database = tenant_database
    
    async def sync_person(self, person: Person) -> None:
        """Sync a single person to Neo4j"""
        await create_person_node(
            database=self.tenant_database,
            person_id=person.id,
            name=person.name,
            generation=person.generation_id,
            gender=person.gender,
            courtesy_name=person.courtesy_name,
            art_name=person.art_name,
            birth_year=person.birth_year,
            death_year=person.death_year,
            avatar=person.avatar,
        )
    
    async def sync_relationship(
        self,
        parent_id: Optional[UUID],
        child_id: UUID
    ) -> None:
        """Sync parent-child relationship"""
        if parent_id:
            await create_father_child_relationship(
                database=self.tenant_database,
                father_id=parent_id,
                child_id=child_id
            )
    
    async def sync_spouse_relation(self, relation: SpouseRelation) -> None:
        """Sync spouse relationship"""
        await create_spouse_relationship(
            database=self.tenant_database,
            husband_id=relation.husband_id,
            wife_id=relation.wife_id,
            relation_type=relation.relation_type,
            order=relation.sort_order
        )
    
    async def sync_all(self, db: AsyncSession) -> None:
        """Sync all data from PostgreSQL to Neo4j"""
        
        # Sync all persons
        print("Syncing persons to Neo4j...")
        stmt = select(Person)
        result = await db.execute(stmt)
        persons = result.scalars().all()
        
        for person in persons:
            await self.sync_person(person)
            print(f"  Synced: {person.name}")
        
        # Sync parent-child relationships
        print("Syncing parent-child relationships...")
        for person in persons:
            if person.father_id:
                await self.sync_relationship(person.father_id, person.id)
        
        # Sync spouse relationships
        print("Syncing spouse relationships...")
        stmt = select(SpouseRelation)
        result = await db.execute(stmt)
        relations = result.scalars().all()
        
        for relation in relations:
            await self.sync_spouse_relation(relation)
        
        print("✅ Full sync complete!")
    
    async def rebuild_graph(self, db: AsyncSession) -> None:
        """Clear and rebuild the entire graph"""
        client = await get_neo4j_client()
        
        # Clear existing data
        async with client.get_session(self.tenant_database) as session:
            await session.run(f"MATCH (n:{self.tenant_database}) DETACH DELETE n")
        
        # Re-sync everything
        await self.sync_all(db)


async def sync_tenant_to_neo4j(tenant_schema: str, tenant_db: str) -> None:
    """Main function to sync a tenant's data to Neo4j"""
    
    from app.core.database import tenant_session
    
    sync_service = GraphSyncService(tenant_database=tenant_db)
    
    async with tenant_session(tenant_schema) as session:
        await sync_service.rebuild_graph(session)


async def quick_sync_person(tenant_schema: str, tenant_db: str, person_id: UUID) -> None:
    """Quick sync a single person"""
    
    from app.core.database import tenant_session
    from sqlalchemy import select
    
    sync_service = GraphSyncService(tenant_database=tenant_db)
    
    async with tenant_session(tenant_schema) as session:
        stmt = select(Person).where(Person.id == person_id)
        result = await session.execute(stmt)
        person = result.scalar_one_or_none()
        
        if person:
            await sync_service.sync_person(person)
            
            # Sync parents
            if person.father_id:
                await sync_service.sync_relationship(person.father_id, person.id)
            
            print(f"✅ Synced person: {person.name}")


async def main():
    """CLI for syncing data"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python -m scripts.sync_neo4j <tenant_schema>")
        print("Example: python -m scripts.sync_neo4j tenant_liu_qianzheng")
        sys.exit(1)
    
    tenant_schema = sys.argv[1]
    tenant_db = f"tenant_{tenant_schema.replace('tenant_', '')}"
    
    print(f"Syncing {tenant_schema} to Neo4j database: {tenant_db}")
    await sync_tenant_to_neo4j(tenant_schema, tenant_db)


if __name__ == "__main__":
    asyncio.run(main())