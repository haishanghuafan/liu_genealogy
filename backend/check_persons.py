import asyncio
from app.core.database import db_manager
from sqlalchemy import select, func
from app.models.tenant import Person

async def check():
    db_manager.init_default_engine()
    sm = db_manager.get_session_maker("liushipu")
    async with sm() as s:
        result = await s.execute(select(func.count(Person.id)))
        count = result.scalar()
        print(f"Total persons: {count}")

        result = await s.execute(select(Person).where(Person.father_id == None).limit(5))
        roots = result.scalars().all()
        print(f"Persons with no father (roots): {len(roots)}")
        for p in roots:
            print(f"  - {p.name} (id={p.id}, generation_id={p.generation_id})")

asyncio.run(check())
