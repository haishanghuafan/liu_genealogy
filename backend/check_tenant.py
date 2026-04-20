import asyncio
from app.core.database import db_manager
from sqlalchemy import select
from app.models.system import Tenant

async def check():
    db_manager.init_default_engine()
    sm = db_manager.get_session_maker("public")
    async with sm() as s:
        result = await s.execute(select(Tenant))
        tenants = result.scalars().all()
        for t in tenants:
            print(f"Slug: {t.slug}, Schema: {t.schema_name}")

asyncio.run(check())
