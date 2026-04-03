"""
External services management with graceful fallback
"""
from typing import Optional

from app.core.config import settings


class Neo4jService:
    """Neo4j graph database service with optional support"""
    
    _instance: Optional["Neo4jService"] = None
    _driver = None
    _available: bool = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    async def connect(self) -> bool:
        """Connect to Neo4j, return True if successful"""
        try:
            from neo4j import AsyncGraphDatabase
            
            self._driver = AsyncGraphDatabase.driver(
                settings.neo4j_uri,
                auth=(settings.neo4j_user, settings.neo4j_password)
            )
            # Test connection
            await self._driver.verify_connectivity()
            self._available = True
            print(f"[OK] Neo4j connected: {settings.neo4j_uri}")
            return True
        except Exception as e:
            self._available = False
            print(f"[--] Neo4j not available: {e}")
            print("    Graph queries will use SQL fallback (limited functionality)")
            return False
    
    async def close(self) -> None:
        """Close Neo4j connection"""
        if self._driver:
            await self._driver.close()
            self._driver = None
            self._available = False
    
    @property
    def is_available(self) -> bool:
        """Check if Neo4j is available"""
        return self._available
    
    async def execute_query(self, query: str, parameters: dict = None):
        """Execute a Cypher query"""
        if not self._available:
            raise RuntimeError("Neo4j is not available")
        
        async with self._driver.session() as session:
            result = await session.run(query, parameters or {})
            return [record async for record in result]
    
    # ============ Graph Query Methods ============
    
    async def get_ancestor_chain(self, person_id: str, max_depth: int = 10) -> list[dict]:
        """Get ancestor chain (parents, grandparents, etc.)"""
        if not self._available:
            return []
        
        query = """
        MATCH path = (p:Person {id: $person_id})-[:CHILD_OF*1..{max_depth}]->(ancestor:Person)
        RETURN ancestor.id as id, ancestor.name as name, 
               length(path) as generation, relationships(path) as rels
        ORDER BY generation
        """
        results = await self.execute_query(
            query.replace("{max_depth}", str(max_depth)),
            {"person_id": person_id}
        )
        return [dict(r) for r in results]
    
    async def get_descendant_chain(self, person_id: str, max_depth: int = 10) -> list[dict]:
        """Get descendant chain (children, grandchildren, etc.)"""
        if not self._available:
            return []
        
        query = """
        MATCH path = (p:Person {id: $person_id})<-[:CHILD_OF*1..{max_depth}]-(descendant:Person)
        RETURN descendant.id as id, descendant.name as name,
               length(path) as generation
        ORDER BY generation
        """
        results = await self.execute_query(
            query.replace("{max_depth}", str(max_depth)),
            {"person_id": person_id}
        )
        return [dict(r) for r in results]
    
    async def find_relationship_path(self, person1_id: str, person2_id: str) -> list[dict]:
        """Find relationship path between two persons"""
        if not self._available:
            return []
        
        query = """
        MATCH path = shortestPath(
            (p1:Person {id: $person1_id})-[*]-(p2:Person {id: $person2_id})
        )
        RETURN [n in nodes(path) | {id: n.id, name: n.name}] as path
        """
        results = await self.execute_query(query, {
            "person1_id": person1_id,
            "person2_id": person2_id
        })
        return results[0]["path"] if results else []
    
    async def sync_person(self, person_data: dict) -> None:
        """Sync person to Neo4j graph"""
        if not self._available:
            return
        
        query = """
        MERGE (p:Person {id: $id})
        SET p.name = $name, p.generation = $generation, p.branch = $branch
        """
        await self.execute_query(query, person_data)
    
    async def sync_relationship(self, child_id: str, parent_id: str) -> None:
        """Sync parent-child relationship to Neo4j"""
        if not self._available:
            return
        
        query = """
        MATCH (child:Person {id: $child_id})
        MATCH (parent:Person {id: $parent_id})
        MERGE (child)-[:CHILD_OF]->(parent)
        """
        await self.execute_query(query, {
            "child_id": child_id,
            "parent_id": parent_id
        })


class RedisService:
    """Redis cache service with optional support"""
    
    _instance: Optional["RedisService"] = None
    _client = None
    _available: bool = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    async def connect(self) -> bool:
        """Connect to Redis, return True if successful"""
        try:
            import redis.asyncio as redis
            
            self._client = redis.from_url(str(settings.redis_url))
            await self._client.ping()
            self._available = True
            print(f"[OK] Redis connected: {settings.redis_url}")
            return True
        except Exception as e:
            self._available = False
            print(f"[--] Redis not available: {e}")
            print("    Caching will be disabled")
            return False
    
    async def close(self) -> None:
        """Close Redis connection"""
        if self._client:
            await self._client.close()
            self._client = None
            self._available = False
    
    @property
    def is_available(self) -> bool:
        """Check if Redis is available"""
        return self._available
    
    async def get(self, key: str) -> Optional[str]:
        """Get value from cache"""
        if not self._available:
            return None
        return await self._client.get(key)
    
    async def set(self, key: str, value: str, expire: int = 3600) -> None:
        """Set value in cache with expiration"""
        if not self._available:
            return
        await self._client.setex(key, expire, value)
    
    async def delete(self, key: str) -> None:
        """Delete key from cache"""
        if not self._available:
            return
        await self._client.delete(key)


class MeilisearchService:
    """Meilisearch full-text search service with optional support"""
    
    _instance: Optional["MeilisearchService"] = None
    _client = None
    _available: bool = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    async def connect(self) -> bool:
        """Connect to Meilisearch, return True if successful"""
        try:
            from meilisearch_python_async import Client
            
            self._client = Client(
                settings.meilisearch_url,
                settings.meilisearch_api_key
            )
            await self._client.health()
            self._available = True
            print(f"[OK] Meilisearch connected: {settings.meilisearch_url}")
            return True
        except Exception as e:
            self._available = False
            print(f"[--] Meilisearch not available: {e}")
            print("    Search will use SQL LIKE fallback")
            return False
    
    async def close(self) -> None:
        """Close Meilisearch connection"""
        if self._client:
            await self._client.aclose()
            self._client = None
            self._available = False
    
    @property
    def is_available(self) -> bool:
        """Check if Meilisearch is available"""
        return self._available
    
    async def index_person(self, index_name: str, person_data: dict) -> None:
        """Index a person document"""
        if not self._available:
            return
        
        index = self._client.index(index_name)
        await index.add_documents([person_data])
    
    async def search(self, index_name: str, query: str, limit: int = 20) -> list[dict]:
        """Search for documents"""
        if not self._available:
            return []
        
        index = self._client.index(index_name)
        results = await index.search(query, limit=limit)
        return results.hits if results else []


# Global service instances
neo4j_service = Neo4jService()
redis_service = RedisService()
meilisearch_service = MeilisearchService()


async def connect_services() -> dict[str, bool]:
    """Connect all external services, return status dict"""
    results = {}
    
    # These are all optional - failures won't prevent app startup
    results["neo4j"] = await neo4j_service.connect()
    results["redis"] = await redis_service.connect()
    results["meilisearch"] = await meilisearch_service.connect()
    
    return results


async def disconnect_services() -> None:
    """Disconnect all external services"""
    await neo4j_service.close()
    await redis_service.close()
    await meilisearch_service.close()
