"""
Initialize Liu Family Genealogy Database
"""
import asyncio
import sys
import uuid
from datetime import datetime

sys.path.insert(0, ".")

from app.core.database import db_manager, Base
from app.core.security import get_password_hash
from app.models import Tenant, User, TenantUser
from app.models.tenant import Person, Generation, Branch, SpouseRelation


async def init_database():
    db_manager.init_default_engine()

    async with db_manager._default_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    print("[OK] Database tables created")


async def create_tenant():
    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy import select

    session_maker = db_manager.get_session_maker("public")
    async with session_maker() as session:
        tenant_slug = "liushipu"

        stmt = select(Tenant).where(Tenant.slug == tenant_slug)
        result = await session.execute(stmt)
        existing = result.scalar_one_or_none()

        if existing:
            print(f"[OK] Tenant '{tenant_slug}' already exists")
            return existing

        tenant = Tenant(
            id=uuid.uuid4(),
            name="刘氏族谱",
            slug=tenant_slug,
            surname="刘",
            is_public=True,
            is_active=True,
            plan="free",
            schema_name="liushipu",
            neo4j_database=f"tenant_{tenant_slug}",
        )
        session.add(tenant)

        admin_user = User(
            id=uuid.uuid4(),
            email="admin@liushipu.com",
            password_hash=get_password_hash("admin123"),
            nickname="管理员",
            system_role="admin",
        )
        session.add(admin_user)
        await session.flush()

        tenant_user = TenantUser(
            tenant_id=tenant.id,
            user_id=admin_user.id,
            role="owner",
        )
        session.add(tenant_user)

        await session.commit()
        print(f"[OK] Tenant '{tenant_slug}' created with admin user")
        print(f"     Email: admin@liushipu.com")
        print(f"     Password: admin123")

        return tenant


async def import_excel_data(tenant: Tenant):
    import pandas as pd
    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy import select

    excel_path = "d:/GitHub/liu_genealogy/docs/刘氏族谱资料/genealogy_data.xlsx"

    try:
        df_persons = pd.read_excel(excel_path, sheet_name="人物")
        df_generations = pd.read_excel(excel_path, sheet_name="世代")
        df_branches = pd.read_excel(excel_path, sheet_name="支系")
        df_spouses = pd.read_excel(excel_path, sheet_name="配偶关系")
        print(f"[OK] Read Excel: {len(df_persons)} persons, {len(df_generations)} generations, {len(df_branches)} branches, {len(df_spouses)} spouses")
    except FileNotFoundError:
        print(f"[!] Excel file not found: {excel_path}")
        return

    session_maker = db_manager.get_session_maker("public")
    async with session_maker() as session:
        gen_map = {}
        for _, row in df_generations.iterrows():
            if pd.notna(row.get("世代数")):
                gen_num = int(row["世代数"])
                gen_name = str(row["世代名称"]) if pd.notna(row.get("世代名称")) else f"第{gen_num}世"
                gen = Generation(
                    number=gen_num,
                    name=gen_name,
                    description=str(row["描述"]) if pd.notna(row.get("描述")) else None,
                )
                session.add(gen)
                await session.flush()
                gen_map[gen_name] = gen.id
                gen_map[gen_num] = gen.id

        await session.flush()
        print(f"[OK] Imported {len(gen_map)} generations")

        branch_map = {}
        for _, row in df_branches.iterrows():
            if pd.notna(row.get("支系名称")):
                branch_name = str(row["支系名称"])
                branch = Branch(
                    name=branch_name,
                    description=str(row["描述"]) if pd.notna(row.get("描述")) else None,
                )
                session.add(branch)
                await session.flush()
                branch_map[branch_name] = branch.id

        await session.flush()
        print(f"[OK] Imported {len(branch_map)} branches")

        name_to_person = {}
        skipped = 0

        for _, row in df_persons.iterrows():
            name = row.get("姓名")
            if not name or pd.isna(name):
                skipped += 1
                continue

            gender_val = row.get("性别", "男")
            gender = "M" if str(gender_val).strip() in ["男", "M"] else "F"

            is_spouse = str(row.get("是否为外族配偶", "否")).strip() == "是"
            if is_spouse:
                skipped += 1
                continue

            gen_name = None
            gen_id = None
            if pd.notna(row.get("世代名称")):
                gen_name = str(row["世代名称"]).strip()
                gen_id = gen_map.get(gen_name)

            branch_name = None
            branch_id = None
            if pd.notna(row.get("所属支系")):
                branch_name = str(row["所属支系"]).strip()
                branch_id = branch_map.get(branch_name)

            person = Person(
                id=uuid.uuid4(),
                name=str(name).strip(),
                gender=gender,
                generation_id=gen_id,
                courtesy_name=str(row["字"]) if pd.notna(row.get("字")) else None,
                art_name=str(row["号"]) if pd.notna(row.get("号")) else None,
                alias=str(row["别名"]) if pd.notna(row.get("别名")) else None,
                generation_char=str(row["辈份字"]) if pd.notna(row.get("辈份字")) else None,
                branch_id=branch_id,
                father_id=None,
                mother_id=None,
                birth_year=int(row["出生年份"]) if pd.notna(row.get("出生年份")) else None,
                death_year=int(row["逝世年份"]) if pd.notna(row.get("逝世年份")) else None,
                birth_place=str(row["出生地"]) if pd.notna(row.get("出生地")) else None,
                burial_place=str(row["葬地"]) if pd.notna(row.get("葬地")) else None,
                burial_fengshui=str(row["墓形/风水"]) if pd.notna(row.get("墓形/风水")) else None,
                burial_direction=str(row["坐向"]) if pd.notna(row.get("坐向")) else None,
                biography=str(row["生平简介"]) if pd.notna(row.get("生平简介")) else None,
                achievements=str(row["主要事迹"]) if pd.notna(row.get("主要事迹")) else None,
                descendants_location=str(row["后裔分布"]) if pd.notna(row.get("后裔分布")) else None,
                notes=str(row["备注"]) if pd.notna(row.get("备注")) else None,
                sort_order=int(row["排序"]) if pd.notna(row.get("排序")) else 0,
            )
            session.add(person)
            name_to_person[str(name).strip()] = person

        await session.commit()
        print(f"[OK] Imported {len(name_to_person)} persons, skipped {skipped}")

        spouse_count = 0
        for _, row in df_spouses.iterrows():
            husband_name = row.get("丈夫姓名")
            wife_name = row.get("妻子姓名")

            if pd.isna(husband_name) or pd.isna(wife_name):
                continue

            husband = name_to_person.get(str(husband_name).strip())
            wife = name_to_person.get(str(wife_name).strip())

            if husband and wife:
                spouse_rel = SpouseRelation(
                    id=uuid.uuid4(),
                    husband_id=husband.id,
                    wife_id=wife.id,
                    relation_type=str(row["关系类型"]) if pd.notna(row.get("关系类型")) else "marriage",
                    source_info=str(row["配偶来源信息"]) if pd.notna(row.get("配偶来源信息")) else None,
                    sort_order=int(row["排序（第几任）"]) if pd.notna(row.get("排序（第几任）")) else 1,
                )
                session.add(spouse_rel)
                spouse_count += 1

        await session.commit()
        print(f"[OK] Created {spouse_count} spouse relations")

        father_count = 0
        mother_count = 0
        for _, row in df_persons.iterrows():
            name = row.get("姓名")
            if not name or pd.isna(name):
                continue

            person = name_to_person.get(str(name).strip())
            if not person:
                continue

            father_name = row.get("父亲姓名")
            if father_name and pd.notna(father_name):
                father = name_to_person.get(str(father_name).strip())
                if father:
                    person.father_id = father.id
                    father_count += 1

            mother_name = row.get("母亲姓名")
            if mother_name and pd.notna(mother_name):
                mother = name_to_person.get(str(mother_name).strip())
                if mother:
                    person.mother_id = mother.id
                    mother_count += 1

        await session.commit()
        print(f"[OK] Set {father_count} father relations, {mother_count} mother relations")


async def main():
    print("=" * 50)
    print("Initializing Liu Family Genealogy Database")
    print("=" * 50)

    await init_database()
    tenant = await create_tenant()
    await import_excel_data(tenant)

    print("=" * 50)
    print("Done!")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())
