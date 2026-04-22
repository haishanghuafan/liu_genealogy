"""
System initialization script - creates demo data for all feature verification

Usage:
    cd backend
    .\venv\Scripts\python.exe -m app.scripts.init_demo_data
"""
import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import db_manager, Base
from app.core.permissions import SYSTEM_PERMISSIONS, BUILTIN_ROLES, BUILTIN_TENANT_ROLES
from app.models.system import (
    User, Tenant, TenantUser,
    Permission, Role, RolePermission, Subscription,
)
from app.models.tenant import Generation, Branch, Person, SpouseRelation


# ============ Password hash helper ============

def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    import bcrypt
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


# ============ System-level initialization ============

async def init_permissions(db: AsyncSession):
    """Initialize permissions and built-in roles"""
    print("  Initializing permissions...")
    
    # Seed permissions
    existing_codes = set()
    stmt = select(Permission.code)
    result = await db.execute(stmt)
    existing_codes = set(result.scalars().all())
    
    new_perms = 0
    for perm_data in SYSTEM_PERMISSIONS:
        if perm_data["code"] not in existing_codes:
            perm = Permission(
                code=perm_data["code"],
                name=perm_data["name"],
                group=perm_data["group"],
                description=perm_data.get("description"),
                resource_type=perm_data.get("resource_type", "system"),
            )
            db.add(perm)
            new_perms += 1
    
    await db.flush()
    
    # Get all permissions for lookup
    perm_stmt = select(Permission)
    perm_result = await db.execute(perm_stmt)
    all_perms = {p.code: p for p in perm_result.scalars().all()}
    
    # Seed built-in system roles
    new_roles = 0
    for role_data in BUILTIN_ROLES:
        stmt = select(Role).where(Role.code == role_data["code"])
        result = await db.execute(stmt)
        existing = result.scalar_one_or_none()
        
        if existing:
            continue
        
        role = Role(
            name=role_data["name"],
            code=role_data["code"],
            scope=role_data["scope"],
            description=role_data["description"],
            is_builtin=True,
        )
        db.add(role)
        await db.flush()
        
        for perm_code in role_data.get("permissions", []):
            if perm_code in all_perms:
                rp = RolePermission(role_id=role.id, permission_id=all_perms[perm_code].id)
                db.add(rp)
        
        new_roles += 1
    
    # Seed built-in tenant roles
    for role_data in BUILTIN_TENANT_ROLES:
        stmt = select(Role).where(Role.code == role_data["code"])
        result = await db.execute(stmt)
        existing = result.scalar_one_or_none()
        
        if existing:
            continue
        
        role = Role(
            name=role_data["name"],
            code=role_data["code"],
            scope="tenant",
            description=role_data["description"],
            is_builtin=True,
        )
        db.add(role)
        await db.flush()
        
        for perm_code in role_data.get("permissions", []):
            if perm_code in all_perms:
                rp = RolePermission(role_id=role.id, permission_id=all_perms[perm_code].id)
                db.add(rp)
        
        new_roles += 1
    
    await db.commit()
    print(f"    Created {new_perms} permissions, {new_roles} roles")


async def init_users(db: AsyncSession) -> dict:
    """Create demo users and return their IDs"""
    print("  Creating users...")
    
    users_data = [
        {
            "email": "admin@liushipu.com",
            "nickname": "系统管理员",
            "password": "admin123",
            "system_role": "super_admin",
        },
        {
            "email": "operator@liushipu.com",
            "nickname": "运营人员",
            "password": "operator123",
            "system_role": "operator",
        },
        # Tenant 1 users
        {
            "email": "zhangsan@liushipu.com",
            "nickname": "张三",
            "password": "user123",
            "system_role": "user",
        },
        {
            "email": "lisi@liushipu.com",
            "nickname": "李四",
            "password": "user123",
            "system_role": "user",
        },
        {
            "email": "wangwu@liushipu.com",
            "nickname": "王五",
            "password": "user123",
            "system_role": "user",
        },
        # Tenant 2 users
        {
            "email": "zhaoliu@liushipu.com",
            "nickname": "赵六",
            "password": "user123",
            "system_role": "user",
        },
        {
            "email": "sunqi@liushipu.com",
            "nickname": "孙七",
            "password": "user123",
            "system_role": "user",
        },
        {
            "email": "zhouba@liushipu.com",
            "nickname": "周八",
            "password": "user123",
            "system_role": "user",
        },
        {
            "email": "wujiu@liushipu.com",
            "nickname": "吴九",
            "password": "user123",
            "system_role": "user",
        },
    ]
    
    user_ids = {}
    for u in users_data:
        stmt = select(User).where(User.email == u["email"])
        result = await db.execute(stmt)
        existing = result.scalar_one_or_none()
        
        if existing:
            user_ids[u["email"]] = existing.id
            print(f"    User {u['email']} already exists")
            continue
        
        user = User(
            email=u["email"],
            nickname=u["nickname"],
            password_hash=hash_password(u["password"]),
            system_role=u["system_role"],
            email_verified=True,
        )
        db.add(user)
        await db.flush()
        user_ids[u["email"]] = user.id
        print(f"    Created user: {u['email']}")
    
    await db.commit()
    return user_ids


async def init_tenants(db: AsyncSession) -> dict:
    """Create demo tenants and return their IDs"""
    print("  Creating tenants...")
    
    tenants_data = [
        {
            "name": "刘氏族谱",
            "slug": "liu",
            "surname": "刘",
            "plan": "professional",
            "max_members": 50,
            "max_persons": 1000,
            "max_storage_mb": 1000,
            "is_public": True,
        },
        {
            "name": "张氏族谱",
            "slug": "zhang",
            "surname": "张",
            "plan": "enterprise",
            "max_members": 100,
            "max_persons": 5000,
            "max_storage_mb": 5000,
            "is_public": True,
        },
    ]
    
    tenant_ids = {}
    for t in tenants_data:
        stmt = select(Tenant).where(Tenant.slug == t["slug"])
        result = await db.execute(stmt)
        existing = result.scalar_one_or_none()
        
        if existing:
            tenant_ids[t["slug"]] = existing.id
            print(f"    Tenant {t['slug']} already exists")
            continue
        
        tenant = Tenant(
            name=t["name"],
            slug=t["slug"],
            surname=t["surname"],
            schema_name=f"tenant_{t['slug']}",
            neo4j_database=f"genealogy_{t['slug']}",
            plan=t["plan"],
            max_members=t["max_members"],
            max_persons=t["max_persons"],
            max_storage_mb=t["max_storage_mb"],
            is_public=t["is_public"],
        )
        db.add(tenant)
        await db.flush()
        tenant_ids[t["slug"]] = tenant.id
        print(f"    Created tenant: {t['name']}")
    
    await db.commit()
    return tenant_ids


async def init_tenant_users(db: AsyncSession, user_ids: dict, tenant_ids: dict):
    """Create tenant-user relationships with roles"""
    print("  Creating tenant-user relationships...")
    
    tenant_users_data = [
        # Tenant 1 (liu) - 2 members, 1 reviewer
        {
            "user_email": "zhangsan@liushipu.com",
            "tenant_slug": "liu",
            "role": "tenant_admin",
        },
        {
            "user_email": "lisi@liushipu.com",
            "tenant_slug": "liu",
            "role": "member",
        },
        {
            "user_email": "wangwu@liushipu.com",
            "tenant_slug": "liu",
            "role": "reviewer",
        },
        # Tenant 2 (zhang) - 3 members, 1 reviewer, 1 editor
        {
            "user_email": "zhaoliu@liushipu.com",
            "tenant_slug": "zhang",
            "role": "tenant_admin",
        },
        {
            "user_email": "sunqi@liushipu.com",
            "tenant_slug": "zhang",
            "role": "member",
        },
        {
            "user_email": "zhouba@liushipu.com",
            "tenant_slug": "zhang",
            "role": "member",
        },
        {
            "user_email": "wujiu@liushipu.com",
            "tenant_slug": "zhang",
            "role": "editor",
        },
    ]
    
    for tu in tenant_users_data:
        user_id = user_ids[tu["user_email"]]
        tenant_id = tenant_ids[tu["tenant_slug"]]
        
        stmt = select(TenantUser).where(
            TenantUser.user_id == user_id,
            TenantUser.tenant_id == tenant_id,
        )
        result = await db.execute(stmt)
        existing = result.scalar_one_or_none()
        
        if existing:
            print(f"    TenantUser {tu['user_email']}@{tu['tenant_slug']} already exists")
            continue
        
        tenant_user = TenantUser(
            user_id=user_id,
            tenant_id=tenant_id,
            role=tu["role"],
        )
        db.add(tenant_user)
        print(f"    Created: {tu['user_email']} as {tu['role']} in {tu['tenant_slug']}")
    
    await db.commit()


async def init_subscriptions(db: AsyncSession, tenant_ids: dict):
    """Create demo subscriptions"""
    print("  Creating subscriptions...")
    
    from datetime import datetime, timezone, timedelta
    
    for slug, tenant_id in tenant_ids.items():
        stmt = select(Subscription).where(Subscription.tenant_id == tenant_id)
        result = await db.execute(stmt)
        existing = result.scalar_one_or_none()
        
        if existing:
            print(f"    Subscription for {slug} already exists")
            continue
        
        sub = Subscription(
            tenant_id=tenant_id,
            plan="professional" if slug == "liu" else "enterprise",
            status="active",
            started_at=datetime.now(timezone.utc),
            expires_at=datetime.now(timezone.utc) + timedelta(days=365),
        )
        db.add(sub)
        print(f"    Created subscription for {slug}")
    
    await db.commit()


# ============ Tenant-level data initialization ============

async def init_tenant1_data(db: AsyncSession, tenant_id: UUID):
    """
    Tenant 1 (刘氏): 1 branch, 3 generations, 20+ persons
    Structure:
      Generation 1: 刘太祖 (founder)
      Generation 2: 刘太宗, 刘世宗 (2 sons)
      Generation 3: 4-5 grandsons per father
    """
    print("  Initializing Tenant 1 (刘氏) data...")
    
    # Create generations
    generations = []
    for i, (num, name) in enumerate([
        (1, "太祖"),
        (2, "太宗"),
        (3, "世宗"),
    ]):
        stmt = select(Generation).where(Generation.number == num)
        result = await db.execute(stmt)
        existing = result.scalar_one_or_none()
        
        if existing:
            generations.append(existing)
        else:
            gen = Generation(number=num, name=name)
            db.add(gen)
            await db.flush()
            generations.append(gen)
    
    # Create branch
    stmt = select(Branch).where(Branch.name == "主支")
    result = await db.execute(stmt)
    branch = result.scalar_one_or_none()
    
    if not branch:
        branch = Branch(name="主支", description="刘氏主支")
        db.add(branch)
        await db.flush()
    
    # Create persons - Generation 1
    liu_taizu = Person(
        name="刘太祖",
        gender="M",
        generation_id=generations[0].number,
        generation_char="祖",
        birth_year=1850,
        death_year=1920,
        birth_place="湖南省长沙市",
        biography="刘氏始祖，白手起家，创立家业",
        branch_id=branch.id,
        branch_name="主支",
        sort_order=1,
    )
    db.add(liu_taizu)
    await db.flush()
    
    # Wife of founder
    liu_taizu_wife = Person(
        name="王氏",
        gender="F",
        is_outsider=True,
        generation_id=generations[0].number,
        birth_year=1855,
        death_year=1930,
        birth_place="湖南省长沙市",
        branch_id=branch.id,
        branch_name="主支",
        sort_order=2,
    )
    db.add(liu_taizu_wife)
    await db.flush()
    
    # Spouse relation
    sr = SpouseRelation(husband_id=liu_taizu.id, wife_id=liu_taizu_wife.id)
    db.add(sr)
    await db.flush()
    
    # Generation 2 - 2 sons
    liu_taizong = Person(
        name="刘太宗",
        gender="M",
        generation_id=generations[1].number,
        generation_char="宗",
        father_id=liu_taizu.id,
        mother_id=liu_taizu_wife.id,
        birth_year=1875,
        death_year=1950,
        birth_place="湖南省长沙市",
        biography="长子，继承家业",
        branch_id=branch.id,
        branch_name="主支",
        sort_order=3,
    )
    db.add(liu_taizong)
    await db.flush()
    
    liu_shizong = Person(
        name="刘世宗",
        gender="M",
        generation_id=generations[1].number,
        generation_char="宗",
        father_id=liu_taizu.id,
        mother_id=liu_taizu_wife.id,
        birth_year=1878,
        death_year=1955,
        birth_place="湖南省长沙市",
        biography="次子，外出经商",
        branch_id=branch.id,
        branch_name="主支",
        sort_order=4,
    )
    db.add(liu_shizong)
    await db.flush()
    
    # Wives for generation 2
    liu_taizong_wife = Person(
        name="李氏",
        gender="F",
        is_outsider=True,
        generation_id=generations[1].number,
        birth_year=1880,
        death_year=1960,
        branch_id=branch.id,
        branch_name="主支",
        sort_order=5,
    )
    db.add(liu_taizong_wife)
    await db.flush()
    
    sr2 = SpouseRelation(husband_id=liu_taizong.id, wife_id=liu_taizong_wife.id)
    db.add(sr2)
    await db.flush()
    
    liu_shizong_wife = Person(
        name="陈氏",
        gender="F",
        is_outsider=True,
        generation_id=generations[1].number,
        birth_year=1882,
        death_year=1962,
        branch_id=branch.id,
        branch_name="主支",
        sort_order=6,
    )
    db.add(liu_shizong_wife)
    await db.flush()
    
    sr3 = SpouseRelation(husband_id=liu_shizong.id, wife_id=liu_shizong_wife.id)
    db.add(sr3)
    await db.flush()
    
    # Generation 3 - grandchildren (4 from 太宗, 4 from 世宗)
    grandchildren_data = [
        # 太宗's children
        {"name": "刘世德", "father": liu_taizong.id, "mother": liu_taizong_wife.id, "birth_year": 1900, "sort": 7},
        {"name": "刘世明", "father": liu_taizong.id, "mother": liu_taizong_wife.id, "birth_year": 1903, "sort": 8},
        {"name": "刘世华", "father": liu_taizong.id, "mother": liu_taizong_wife.id, "birth_year": 1906, "sort": 9},
        {"name": "刘世芳", "father": liu_taizong.id, "mother": liu_taizong_wife.id, "birth_year": 1909, "sort": 10},
        # 世宗's children
        {"name": "刘世昌", "father": liu_shizong.id, "mother": liu_shizong_wife.id, "birth_year": 1902, "sort": 11},
        {"name": "刘世荣", "father": liu_shizong.id, "mother": liu_shizong_wife.id, "birth_year": 1905, "sort": 12},
        {"name": "刘世贵", "father": liu_shizong.id, "mother": liu_shizong_wife.id, "birth_year": 1908, "sort": 13},
        {"name": "刘世富", "father": liu_shizong.id, "mother": liu_shizong_wife.id, "birth_year": 1911, "sort": 14},
    ]
    
    for gd in grandchildren_data:
        p = Person(
            name=gd["name"],
            gender="M",
            generation_id=generations[2].number,
            generation_char="世",
            father_id=gd["father"],
            mother_id=gd["mother"],
            birth_year=gd["birth_year"],
            birth_place="湖南省长沙市",
            branch_id=branch.id,
            branch_name="主支",
            sort_order=gd["sort"],
        )
        db.add(p)
        await db.flush()
    
    # Add some more persons to reach 20+
    extra_persons = [
        {"name": "刘世德妻", "gender": "F", "is_outsider": True, "generation_id": generations[2].number, "birth_year": 1902, "sort": 15},
        {"name": "刘世明妻", "gender": "F", "is_outsider": True, "generation_id": generations[2].number, "birth_year": 1905, "sort": 16},
        {"name": "刘世华妻", "gender": "F", "is_outsider": True, "generation_id": generations[2].number, "birth_year": 1908, "sort": 17},
        {"name": "刘世昌妻", "gender": "F", "is_outsider": True, "generation_id": generations[2].number, "birth_year": 1904, "sort": 18},
        {"name": "刘世荣妻", "gender": "F", "is_outsider": True, "generation_id": generations[2].number, "birth_year": 1907, "sort": 19},
        {"name": "刘世贵妻", "gender": "F", "is_outsider": True, "generation_id": generations[2].number, "birth_year": 1910, "sort": 20},
        {"name": "刘世富妻", "gender": "F", "is_outsider": True, "generation_id": generations[2].number, "birth_year": 1913, "sort": 21},
    ]
    
    for ep in extra_persons:
        p = Person(
            name=ep["name"],
            gender=ep["gender"],
            is_outsider=ep["is_outsider"],
            generation_id=ep["generation_id"],
            birth_year=ep["birth_year"],
            birth_place="湖南省长沙市",
            branch_id=branch.id,
            branch_name="主支",
            sort_order=ep["sort"],
        )
        db.add(p)
        await db.flush()
    
    await db.commit()
    print("    Tenant 1 data initialized: 1 branch, 3 generations, 21 persons")


async def init_tenant2_data(db: AsyncSession, tenant_id: UUID):
    """
    Tenant 2 (张氏): 2 branches, 4 generations, 40+ persons
    Structure:
      Branch 1 (主支): 3 generations
      Branch 2 (分支): 3 generations
    """
    print("  Initializing Tenant 2 (张氏) data...")
    
    # Create generations
    generations = []
    for i, (num, name) in enumerate([
        (1, "始祖"),
        (2, "二世"),
        (3, "三世"),
        (4, "四世"),
    ]):
        stmt = select(Generation).where(Generation.number == num)
        result = await db.execute(stmt)
        existing = result.scalar_one_or_none()
        
        if existing:
            generations.append(existing)
        else:
            gen = Generation(number=num, name=name)
            db.add(gen)
            await db.flush()
            generations.append(gen)
    
    # Create branches
    branches = []
    for bname in ["主支", "分支"]:
        stmt = select(Branch).where(Branch.name == bname)
        result = await db.execute(stmt)
        existing = result.scalar_one_or_none()
        
        if existing:
            branches.append(existing)
        else:
            branch = Branch(name=bname, description=f"张氏{bname}")
            db.add(branch)
            await db.flush()
            branches.append(branch)
    
    # Branch 1 - 主支
    zhang_shizu = Person(
        name="张始祖",
        gender="M",
        generation_id=generations[0].number,
        generation_char="始",
        birth_year=1840,
        death_year=1910,
        birth_place="山东省济南市",
        biography="张氏始祖，迁居山东",
        branch_id=branches[0].id,
        branch_name="主支",
        sort_order=1,
    )
    db.add(zhang_shizu)
    await db.flush()
    
    zhang_shizu_wife = Person(
        name="赵氏",
        gender="F",
        is_outsider=True,
        generation_id=generations[0].number,
        birth_year=1845,
        death_year=1920,
        branch_id=branches[0].id,
        branch_name="主支",
        sort_order=2,
    )
    db.add(zhang_shizu_wife)
    await db.flush()
    
    db.add(SpouseRelation(husband_id=zhang_shizu.id, wife_id=zhang_shizu_wife.id))
    await db.flush()
    
    # Generation 2 - 主支
    zhang_ershi_1 = Person(
        name="张二世长",
        gender="M",
        generation_id=generations[1].number,
        generation_char="二",
        father_id=zhang_shizu.id,
        mother_id=zhang_shizu_wife.id,
        birth_year=1865,
        death_year=1940,
        branch_id=branches[0].id,
        branch_name="主支",
        sort_order=3,
    )
    db.add(zhang_ershi_1)
    await db.flush()
    
    zhang_ershi_2 = Person(
        name="张二世次",
        gender="M",
        generation_id=generations[1].number,
        generation_char="二",
        father_id=zhang_shizu.id,
        mother_id=zhang_shizu_wife.id,
        birth_year=1868,
        death_year=1945,
        branch_id=branches[0].id,
        branch_name="主支",
        sort_order=4,
    )
    db.add(zhang_ershi_2)
    await db.flush()
    
    zhang_ershi_1_wife = Person(
        name="孙氏",
        gender="F",
        is_outsider=True,
        generation_id=generations[1].number,
        birth_year=1870,
        branch_id=branches[0].id,
        branch_name="主支",
        sort_order=5,
    )
    db.add(zhang_ershi_1_wife)
    await db.flush()
    
    db.add(SpouseRelation(husband_id=zhang_ershi_1.id, wife_id=zhang_ershi_1_wife.id))
    await db.flush()
    
    zhang_ershi_2_wife = Person(
        name="周氏",
        gender="F",
        is_outsider=True,
        generation_id=generations[1].number,
        birth_year=1872,
        branch_id=branches[0].id,
        branch_name="主支",
        sort_order=6,
    )
    db.add(zhang_ershi_2_wife)
    await db.flush()
    
    db.add(SpouseRelation(husband_id=zhang_ershi_2.id, wife_id=zhang_ershi_2_wife.id))
    await db.flush()
    
    # Generation 3 - 主支 (5 children from 长, 5 from 次)
    sort_counter = 7
    for parent, wife in [(zhang_ershi_1, zhang_ershi_1_wife), (zhang_ershi_2, zhang_ershi_2_wife)]:
        for i in range(5):
            p = Person(
                name=f"张三世{'abcdef'[i]}",
                gender="M",
                generation_id=generations[2].number,
                generation_char="三",
                father_id=parent.id,
                mother_id=wife.id,
                birth_year=1890 + i * 3,
                branch_id=branches[0].id,
                branch_name="主支",
                sort_order=sort_counter,
            )
            db.add(p)
            await db.flush()
            sort_counter += 1
    
    # Generation 4 - 主支 (some grandchildren)
    stmt = select(Person).where(Person.generation_id == generations[2].number).limit(4)
    result = await db.execute(stmt)
    gen3_persons = result.scalars().all()
    
    for i, parent in enumerate(gen3_persons[:4]):
        for j in range(3):
            p = Person(
                name=f"张四世{i}{j}",
                gender="M" if j % 2 == 0 else "F",
                generation_id=generations[3].number,
                generation_char="四",
                father_id=parent.id if j % 2 == 0 else None,
                mother_id=None,
                birth_year=1920 + i * 5 + j,
                branch_id=branches[0].id,
                branch_name="主支",
                sort_order=sort_counter,
            )
            db.add(p)
            await db.flush()
            sort_counter += 1
    
    # Branch 2 - 分支
    zhang_fenzhi_shizu = Person(
        name="张分支祖",
        gender="M",
        generation_id=generations[0].number,
        generation_char="始",
        birth_year=1842,
        death_year=1915,
        birth_place="山东省青岛市",
        biography="张氏分支始祖",
        branch_id=branches[1].id,
        branch_name="分支",
        sort_order=sort_counter,
    )
    db.add(zhang_fenzhi_shizu)
    await db.flush()
    sort_counter += 1
    
    zhang_fenzhi_shizu_wife = Person(
        name="吴氏",
        gender="F",
        is_outsider=True,
        generation_id=generations[0].number,
        birth_year=1848,
        branch_id=branches[1].id,
        branch_name="分支",
        sort_order=sort_counter,
    )
    db.add(zhang_fenzhi_shizu_wife)
    await db.flush()
    sort_counter += 1
    
    db.add(SpouseRelation(husband_id=zhang_fenzhi_shizu.id, wife_id=zhang_fenzhi_shizu_wife.id))
    await db.flush()
    
    # Branch 2 - Generation 2
    for i in range(3):
        p = Person(
            name=f"张分支二世{i}",
            gender="M",
            generation_id=generations[1].number,
            generation_char="二",
            father_id=zhang_fenzhi_shizu.id,
            mother_id=zhang_fenzhi_shizu_wife.id,
            birth_year=1870 + i * 4,
            branch_id=branches[1].id,
            branch_name="分支",
            sort_order=sort_counter,
        )
        db.add(p)
        await db.flush()
        sort_counter += 1
    
    # Branch 2 - Generation 3
    stmt = select(Person).where(
        Person.branch_id == branches[1].id,
        Person.generation_id == generations[1].number,
    ).limit(3)
    result = await db.execute(stmt)
    branch2_gen2 = result.scalars().all()
    
    for parent in branch2_gen2:
        for i in range(4):
            p = Person(
                name=f"张分支三世{parent.name[-1]}{i}",
                gender="M",
                generation_id=generations[2].number,
                generation_char="三",
                father_id=parent.id,
                birth_year=1895 + i * 3,
                branch_id=branches[1].id,
                branch_name="分支",
                sort_order=sort_counter,
            )
            db.add(p)
            await db.flush()
            sort_counter += 1
    
    # Add wives for branch 2
    stmt = select(Person).where(
        Person.branch_id == branches[1].id,
        Person.generation_id == generations[1].number,
    )
    result = await db.execute(stmt)
    branch2_gen2_all = result.scalars().all()
    
    for parent in branch2_gen2_all:
        wife = Person(
            name=f"{parent.name}妻",
            gender="F",
            is_outsider=True,
            generation_id=parent.generation_id,
            birth_year=parent.birth_year + 2 if parent.birth_year else 1875,
            branch_id=branches[1].id,
            branch_name="分支",
            sort_order=sort_counter,
        )
        db.add(wife)
        await db.flush()
        db.add(SpouseRelation(husband_id=parent.id, wife_id=wife.id))
        await db.flush()
        sort_counter += 1
    
    await db.commit()
    print(f"    Tenant 2 data initialized: 2 branches, 4 generations, {sort_counter - 1} persons")


# ============ Main initialization ============

async def main():
    print("=" * 60)
    print("  族谱云 - 系统初始化脚本")
    print("=" * 60)
    
    # Initialize database manager
    db_manager.init_default_engine()
    
    # Use system database
    system_db = db_manager.get_session_maker("public")
    
    # Create all tables
    print("\n[0/7] 创建数据库表...")
    async with db_manager.get_engine("public").begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("    数据库表创建完成")
    
    async with system_db() as db:
        # Step 1: Initialize permissions and roles
        print("\n[1/7] 初始化权限和角色...")
        await init_permissions(db)
        
        # Step 2: Create users
        print("\n[2/7] 创建用户...")
        user_ids = await init_users(db)
        
        # Step 3: Create tenants
        print("\n[3/7] 创建租户...")
        tenant_ids = await init_tenants(db)
        
        # Step 4: Create tenant-user relationships
        print("\n[4/7] 创建租户用户关系...")
        await init_tenant_users(db, user_ids, tenant_ids)
        
        # Step 5: Create subscriptions
        print("\n[5/7] 创建订阅...")
        await init_subscriptions(db, tenant_ids)
        
        # Step 6: Initialize tenant-level data
        print("\n[6/7] 初始化租户数据...")
        
        # Tenant 1 data
        liu_tenant_id = tenant_ids["liu"]
        await init_tenant1_data(db, liu_tenant_id)
        
        # Tenant 2 data
        zhang_tenant_id = tenant_ids["zhang"]
        await init_tenant2_data(db, zhang_tenant_id)
    
    print("\n[7/7] 初始化完成！")
    print("\n登录账号：")
    print("  超级管理员: admin@liushipu.com / admin123")
    print("  运营人员:   operator@liushipu.com / operator123")
    print("\n刘氏族谱 (liu):")
    print("  管理员: zhangsan@liushipu.com / user123")
    print("  成员:   lisi@liushipu.com / user123")
    print("  审核员: wangwu@liushipu.com / user123")
    print("\n张氏族谱 (zhang):")
    print("  管理员: zhaoliu@liushipu.com / user123")
    print("  成员:   sunqi@liushipu.com / user123")
    print("  成员:   zhouba@liushipu.com / user123")
    print("  编辑员: wujiu@liushipu.com / user123")
    print("\n访问地址：")
    print("  仪表盘:   http://localhost:3012/dashboard")
    print("  刘氏族谱: http://localhost:3012/t/liu")
    print("  张氏族谱: http://localhost:3012/t/zhang")
    print("  角色管理: http://localhost:3012/admin/roles")
    print("  权限管理: http://localhost:3012/admin/permissions")


if __name__ == "__main__":
    asyncio.run(main())
