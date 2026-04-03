"""
Neo4j client for Genealogy SaaS
"""
from typing import Any, Optional
from uuid import UUID

from neo4j import AsyncGraphDatabase, AsyncDriver, AsyncSession, Record

from app.core.config import settings


class Neo4jClient:
    """Neo4j client for managing genealogy graph data"""
    
    def __init__(self, uri: Optional[str] = None, user: Optional[str] = None, password: Optional[str] = None):
        self._driver: Optional[AsyncDriver] = None
        self.uri = uri or settings.neo4j_uri
        self.user = user or settings.neo4j_user
        self.password = password or settings.neo4j_password
    
    async def connect(self) -> None:
        """Connect to Neo4j"""
        if self._driver is None:
            self._driver = AsyncGraphDatabase.driver(
                self.uri,
                auth=(self.user, self.password)
            )
    
    async def close(self) -> None:
        """Close the connection"""
        if self._driver:
            await self._driver.close()
            self._driver = None
    
    def get_session(self, database: Optional[str] = None) -> AsyncSession:
        """Get a Neo4j session"""
        if self._driver is None:
            raise RuntimeError("Neo4j client not connected. Call connect() first.")
        return self._driver.session(database=database)
    
    async def verify_connectivity(self) -> bool:
        """Verify Neo4j connection"""
        try:
            async with self.get_session() as session:
                result = await session.run("RETURN 1 as test")
                await result.single()
            return True
        except Exception:
            return False


# Global client instance
neo4j_client = Neo4jClient()


async def get_neo4j_client() -> Neo4jClient:
    """Get Neo4j client instance"""
    if neo4j_client._driver is None:
        await neo4j_client.connect()
    return neo4j_client


# ============ Graph Queries ============

async def create_person_node(
    database: str,
    person_id: UUID,
    name: str,
    generation: Optional[int] = None,
    gender: str = "M",
    **kwargs
) -> None:
    """Create a person node in Neo4j"""
    client = await get_neo4j_client()
    
    properties = {
        "id": str(person_id),
        "name": name,
        "generation": generation,
        "gender": gender,
    }
    
    # Add optional properties
    for key, value in kwargs.items():
        if value is not None:
            properties[key] = value
    
    query = f"""
        CREATE (p:Person:{database} {{
            id: $id,
            name: $name,
            generation: $generation,
            gender: $gender
        }})
    """
    
    async with client.get_session(database) as session:
        await session.run(query, properties)


async def create_father_child_relationship(
    database: str,
    father_id: UUID,
    child_id: UUID
) -> None:
    """Create father-child relationship"""
    client = await get_neo4j_client()
    
    query = f"""
        MATCH (father:Person:{database} {{id: $father_id}})
        MATCH (child:Person:{database} {{id: $child_id}})
        CREATE (father)-[r:FATHER_OF]->(child)
        CREATE (child)-[r:CHILD_OF]->(father)
    """
    
    async with client.get_session(database) as session:
        await session.run(query, father_id=str(father_id), child_id=str(child_id))


async def create_spouse_relationship(
    database: str,
    husband_id: UUID,
    wife_id: UUID,
    relation_type: str = "marriage",
    order: int = 1
) -> None:
    """Create spouse relationship"""
    client = await get_neo4j_client()
    
    query = f"""
        MATCH (husband:Person:{database} {{id: $husband_id}})
        MATCH (wife:Person:{database} {{id: $wife_id}})
        CREATE (husband)-[r:MARRIED {{type: $type, order: $order}}]->(wife)
    """
    
    async with client.get_session(database) as session:
        await session.run(
            query,
            husband_id=str(husband_id),
            wife_id=str(wife_id),
            type=relation_type,
            order=order
        )


async def get_family_tree(
    database: str,
    root_id: UUID,
    depth: int = 3
) -> list[dict]:
    """Get family tree starting from a person"""
    client = await get_neo4j_client()
    
    query = f"""
        MATCH path = (root:Person {{id: $root_id}})-[:FATHER_OF|CHILD_OF*0..{depth}]->(descendant)
        WHERE descendant:Allviolet
        RETURN nodes(path) as nodes, relationships(path) as rels
    """
    
    async with client.get_session(database) as session:
        result = await session.run(query, root_id=str(root_id))
        records = await result.data()
        return records


async def get_ancestors(
    database: str,
    person_id: UUID,
    limit: int = 10
) -> list[dict]:
    """Get ancestors of a person"""
    client = await get_neo4j_client()
    
    query = f"""
        MATCH (p:Person {{id: $person_id}})<-[:CHILD_OF*1..]-(ancestor)
        WHERE ancestor:{database}
        RETURN DISTINCT ancestor
        ORDER BY ancestor.generation
        LIMIT $limit
    """
    
    async with client.get_session(database) as session:
        result = await session.run(query, person_id=str(person_id), limit=limit)
        records = await result.data()
        return [r["ancestor"] for r in records]


async def get_descendants(
    database: str,
    person_id: UUID,
    depth: int = 5
) -> list[dict]:
    """Get descendants of a person"""
    client = await get_neo4j_client()
    
    query = f"""
        MATCH (p:Person {{id: $person_id}})-[:FATHER_OF*1..{depth}]->(desc)
        WHERE desc:{database}
        RETURN DISTINCT desc
        ORDER BY desc.generation, desc.name
    """
    
    async with client.get_session(database) as session:
        result = await session.run(query, person_id=str(person_id))
        records = await result.data()
        return [r["desc"] for r in records]


async def get_siblings(
    database: str,
    person_id: UUID
) -> list[dict]:
    """Get siblings of a person"""
    client = await get_neo4j_client()
    
    query = f"""
        MATCH (p:Person {{id: $person_id}})<-[:CHILD_OF]-(parent)-[:FATHER_OF]->(sibling)
        WHERE sibling:{database} AND sibling.id <> $person_id
        RETURN DISTINCT sibling
        ORDER BY sibling.generation, sibling.name
    """
    
    async with client.get_session(database) as session:
        result = await session.run(query, person_id=str(person_id))
        records = await result.data()
        return [r["sibling"] for r in records]


async def get_spouses(
    database: str,
    person_id: UUID
) -> list[dict]:
    """Get spouses of a person"""
    client = await get_neo4j_client()
    
    query = f"""
        MATCH (p:Person {{id: $person_id}})-[r:MARRIED]->(spouse)
        WHERE spouse:{database}
        RETURN spouse, r.type as relation_type, r.order as order
        ORDER BY r.order
    """
    
    async with client.get_session(database) as session:
        result = await session.run(query, person_id=str(person_id))
        records = await result.data()
        return records


async def get_generation_members(
    database: str,
    generation_number: int
) -> list[dict]:
    """Get all members of a specific generation"""
    client = await get_neo4j_client()
    
    query = f"""
        MATCH (p:Person:{database} {{generation: $generation}})
        RETURN p
        ORDER BY p.sort_order, p.name
    """
    
    async with client.get_session(database) as session:
        result = await session.run(query, generation=generation_number)
        records = await result.data()
        return [r["p"] for r in records]


async def search_by_name(
    database: str,
    name: str,
    limit: int = 20
) -> list[dict]:
    """Search persons by name (fuzzy)"""
    client = await get_neo4j_client()
    
    query = f"""
        MATCH (p:Person:{database})
        WHERE p.name CONTAINS $name
           OR p.courtesy_name CONTAINS $name
           OR p.art_name CONTAINS $name
           OR p.alias CONTAINS $name
        RETURN p
        LIMIT $limit
    """
    
    async with client.get_session(database) as session:
        result = await session.run(query, name=name, limit=limit)
        records = await result.data()
        return [r["p"] for r in records]


async def get_tree_structure(
    database: str,
    root_id: UUID,
    max_depth: int = 4
) -> dict:
    """
    Get tree structure for visualization
    Returns nested dictionary suitable for D3.js tree
    """
    client = await get_neo4j_client()
    
    query = f"""
        MATCH path = (root:Person {{id: $root_id}})-[:FATHER_OF*0..{max_depth}]->(child)
        WHERE child:{database}
        WITH root, child, length(path) as depth
        ORDER BY depth, child.name
        RETURN root, collect({{child: child, depth: depth}}) as children
    """
    
    async with client.get_session(database) as session:
        result = await session.run(query, root_id=str(root_id))
        record = await result.single()
        
        if not record:
            return {}
        
        return build_tree_from_records(record["root"], record["children"])


def build_tree_from_records(root: dict, children: list[dict]) -> dict:
    """Build nested tree structure from Neo4j records"""
    
    def build_node(person: dict, depth: int) -> dict:
        node = {
            "id": person.get("id"),
            "name": person.get("name"),
            "generation": person.get("generation"),
            "gender": person.get("gender"),
            "birth_year": person.get("birth_year"),
            "children": []
        }
        
        # Filter children for this node
        child_nodes = [
            c["child"] for c in children 
            if c["depth"] == depth + 1
        ]
        
        node["children"] = [build_node(c, depth + 1) for c in child_nodes]
        
        return node
    
    return build_node(root, 0)


async def get_statistics(database: str) -> dict:
    """Get graph statistics"""
    client = await get_neo4j_client()
    
    queries = {
        "total_persons": f"MATCH (p:Person:{database}) RETURN count(p) as count",
        "generations": f"MATCH (p:Person:{database}) RETURN p.generation as generation, count(p) as count ORDER BY generation",
        "branches": f"MATCH (p:Person:{database})-[:BELONGS_TO]->(b:Branch:{database}) RETURN b.name as branch, count(p) as count",
    }
    
    stats = {}
    
    async with client.get_session(database) as session:
        # Total persons
        result = await session.run(queries["total_persons"])
        record = await result.single()
        stats["total_persons"] = record["count"] if record else 0
        
        # By generation
        result = await session.run(queries["generations"])
        stats["by_generation"] = await result.data()
        
        # By branch
        result = await session.run(queries["branches"])
        stats["by_branch"] = await result.data()
    
    return stats