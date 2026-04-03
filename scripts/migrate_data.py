"""
Migrate data from Django backup to new system
"""
import asyncio
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

import asyncpg


async def migrate_django_data():
    """Migrate data from Django backup to new system"""
    
    backup_dir = Path("C:/Users/vmai/.qclaw/workspace/liu_genealogy/django_backup")
    
    # Connect to PostgreSQL
    conn = await asyncpg.connect(
        host="localhost",
        port=5432,
        user="postgres",
        password="postgres",
        database="genealogy"
    )
    
    try:
        # Set search path to tenant schema
        await conn.execute('SET search_path TO tenant_liu_qianzheng')
        
        # 1. Migrate generations
        print("Migrating generations...")
        generations = await load_json(backup_dir / "content" / "generations.json")
        
        for gen in generations:
            await conn.execute('''
                INSERT INTO generations (id, number, is_spouse, name, description)
                VALUES ($1, $2, $3, $4, $5)
                ON CONFLICT (number, is_spouse) DO UPDATE SET
                    name = EXCLUDED.name,
                    description = EXCLUDED.description
            ''', uuid.uuid4(), gen.get('number'), gen.get('is_spouse', False), gen.get('name'), gen.get('description'))
        
        print(f"✓ Migrated {len(generations)} generations")
        
        # 2. Migrate branches
        print("Migrating branches...")
        branches = await load_json(backup_dir / "content" / "branches.json")
        
        for branch in branches:
            await conn.execute('''
                INSERT INTO branches (id, name, founder_id, description, location)
                VALUES ($1, $2, $3, $4, $5)
            ''', uuid.uuid4(), branch.get('name'), None, branch.get('description'), branch.get('location'))
        
        print(f"✓ Migrated {len(branches)} branches")
        
        # 3. Migrate persons (most important)
        print("Migrating persons...")
        persons = await load_json(backup_dir / "content" / "persons.json")
        
        for person in persons:
            await conn.execute('''
                INSERT INTO persons (
                    id, name, courtesy_name, art_name, alias, generation_char,
                    gender, is_outsider, generation_id, father_id, mother_id, branch_id,
                    birth_year, death_year, birth_place,
                    burial_place, burial_fengshui, burial_direction,
                    biography, achievements, descendants_location, notes,
                    visibility, sort_order, avatar, created_at, updated_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18, $19, $20, $21, $22, $23, $24, $25, $26, $27)
                ON CONFLICT (id) DO UPDATE SET
                    name = EXCLUDED.name,
                    courtesy_name = EXCLUDED.courtesy_name,
                    art_name = EXCLUDED.art_name,
                    alias = EXCLUDED.alias
            ''',
                uuid.UUID(person['id']) if person.get('id') else uuid.uuid4(),
                person.get('name'),
                person.get('courtesy_name'),
                person.get('art_name'),
                person.get('alias'),
                person.get('generation_char'),
                person.get('gender', 'M'),
                person.get('is_outsider', False),
                person.get('generation'),
                uuid.UUID(person['father']) if person.get('father') else None,
                uuid.UUID(person['mother']) if person.get('mother') else None,
                uuid.UUID(person['branch']) if person.get('branch') else None,
                person.get('birth_year'),
                person.get('death_year'),
                person.get('birth_place'),
                person.get('burial_place'),
                person.get('burial_fengshui'),
                person.get('burial_direction'),
                person.get('biography'),
                person.get('achievements'),
                person.get('descendants_location'),
                person.get('notes'),
                person.get('visibility', 'public'),
                person.get('order', 0),
                person.get('avatar'),
                datetime.now(),
                datetime.now()
            )
        
        print(f"✓ Migrated {len(persons)} persons")
        
        # 4. Migrate spouse relations
        print("Migrating spouse relations...")
        spouse_relations = await load_json(backup_dir / "content" / "spouse_relations.json")
        
        for rel in spouse_relations:
            try:
                await conn.execute('''
                    INSERT INTO spouse_relations (id, husband_id, wife_id, relation_type, source_info, sort_order)
                    VALUES ($1, $2, $3, $4, $5, $6)
                ''',
                    uuid.uuid4(),
                    uuid.UUID(rel['husband']) if rel.get('husband') else None,
                    uuid.UUID(rel['wife']) if rel.get('wife') else None,
                    rel.get('relation_type', 'marriage'),
                    rel.get('source_info'),
                    rel.get('order', 1)
                )
            except Exception as e:
                print(f"  Warning: Failed to migrate spouse relation: {e}")
        
        print(f"✓ Migrated {len(spouse_relations)} spouse relations")
        
        print("\n✅ Migration complete!")
        
    finally:
        await conn.close()


async def load_json(path: Path) -> list[dict]:
    """Load JSON file"""
    if not path.exists():
        print(f"  Warning: {path} not found, skipping")
        return []
    
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


async def export_django_to_json():
    """Export Django data to JSON files for migration"""
    
    # This would be run on the Django side
    # For now, just a placeholder
    
    print("""
    To export Django data, run this in Django shell:
    
    from django.core import serializers
    
    # Export generations
    data = serializers.serialize('json', Generation.objects.all())
    with open('content/generations.json', 'w') as f:
        f.write(data)
    
    # Export persons
    data = serializers.serialize('json', Person.objects.all())
    with open('content/persons.json', 'w') as f:
        f.write(data)
    """)


if __name__ == "__main__":
    asyncio.run(migrate_django_data())
