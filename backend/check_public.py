import asyncio
from app.core.database import db_manager
from sqlalchemy import select, func
from app.models.tenant import Person

async def check_public():
    db_manager.init_default_engine()
    sm = db_manager.get_session_maker("public")
    async with sm() as s:
        result = await s.execute(select(func.count(Person.id)))
        count = result.scalar()
        print(f"[public] Total persons: {count}")

asyncio.run(check_public())
