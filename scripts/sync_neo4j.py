"""
Sync data to Neo4j - CLI script
"""
import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from app.services.graph_sync import sync_tenant_to_neo4j


async def main():
    """Sync tenant data to Neo4j"""
    
    if len(sys.argv) < 2:
        print("Usage: python sync_neo4j.py <tenant_slug>")
        print("Example: python sync_neo4j.py liu-qianzheng")
        sys.exit(1)
    
    tenant_slug = sys.argv[1]
    tenant_schema = f"tenant_{tenant_slug.replace('-', '_')}"
    tenant_db = f"tenant_{tenant_slug}"
    
    print(f"🚀 Starting sync for: {tenant_slug}")
    print(f"   Schema: {tenant_schema}")
    print(f"   Neo4j DB: {tenant_db}")
    print()
    
    try:
        await sync_tenant_to_neo4j(tenant_schema, tenant_db)
        print("\n✅ Sync completed successfully!")
    except Exception as e:
        print(f"\n❌ Sync failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())