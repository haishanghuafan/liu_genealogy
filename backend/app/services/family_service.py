"""
Family relationship service - calculate and manage family tree relationships
"""
from typing import Optional
from uuid import UUID

from sqlalchemy import select, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tenant import Person, SpouseRelation, Generation


class FamilyService:
    """Service for calculating family relationships"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_person(self, person_id: UUID) -> Optional[Person]:
        """Get person by ID with related data"""
        stmt = select(Person).where(Person.id == person_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_all_children(self, person: Person) -> list[Person]:
        """
        Get all children of a person (as father or mother)
        """
        # Get children as father
        stmt_father = select(Person).where(Person.father_id == person.id)
        result = await self.db.execute(stmt_father)
        children_as_father = result.scalars().all()
        
        # Get children as mother
        stmt_mother = select(Person).where(Person.mother_id == person.id)
        result = await self.db.execute(stmt_mother)
        children_as_mother = result.scalars().all()
        
        # Combine and sort
        all_children = list(children_as_father) + list(children_as_mother)
        return sorted(all_children, key=lambda x: (x.sort_order, x.id))
    
    async def get_children_by_spouse(
        self, 
        person: Person
    ) -> list[dict]:
        """
        Get children grouped by spouse
        
        Returns list of dicts with:
        - spouse: Person object or None
        - children: list of Person objects
        - relation_type: type of spouse relation
        - order: sort order
        """
        if person.gender == 'M':
            # Get all spouse relations where this person is husband
            stmt = select(SpouseRelation).where(
                SpouseRelation.husband_id == person.id
            ).order_by(SpouseRelation.sort_order)
            result = await self.db.execute(stmt)
            spouse_relations = result.scalars().all()
            
            # Get all children
            all_children = await self.get_all_children(person)
            
            # Group by spouse
            children_by_spouse = []
            for relation in spouse_relations:
                wife = await self.get_person(relation.wife_id)
                if wife:
                    spouse_children = [
                        child for child in all_children 
                        if child.mother_id == relation.wife_id
                    ]
                    children_by_spouse.append({
                        'spouse': wife,
                        'children': spouse_children,
                        'relation_type': relation.relation_type,
                        'order': relation.sort_order
                    })
            
            # Children without mother info
            unknown_mother = [
                child for child in all_children 
                if not child.mother_id
            ]
            if unknown_mother:
                children_by_spouse.append({
                    'spouse': None,
                    'children': unknown_mother,
                    'relation_type': None,
                    'order': 999
                })
            
            return children_by_spouse
            
        else:
            # For female, get relations where she is wife
            stmt = select(SpouseRelation).where(
                SpouseRelation.wife_id == person.id
            ).order_by(SpouseRelation.sort_order)
            result = await self.db.execute(stmt)
            spouse_relations = result.scalars().all()
            
            all_children = await self.get_all_children(person)
            
            children_by_spouse = []
            for relation in spouse_relations:
                husband = await self.get_person(relation.husband_id)
                if husband:
                    spouse_children = [
                        child for child in all_children 
                        if child.father_id == relation.husband_id
                    ]
                    children_by_spouse.append({
                        'spouse': husband,
                        'children': spouse_children,
                        'relation_type': relation.relation_type,
                        'order': relation.sort_order
                    })
            
            unknown_father = [
                child for child in all_children 
                if not child.father_id
            ]
            if unknown_father:
                children_by_spouse.append({
                    'spouse': None,
                    'children': unknown_father,
                    'relation_type': None,
                    'order': 999
                })
            
            return children_by_spouse
    
    async def get_siblings(self, person: Person) -> list[Person]:
        """
        Get siblings (people who share the same father)
        """
        if not person.father_id:
            return []
        
        stmt = select(Person).where(
            and_(
                Person.father_id == person.father_id,
                Person.id != person.id
            )
        ).order_by(Person.sort_order, Person.id)
        
        result = await self.db.execute(stmt)
        return result.scalars().all()
    
    async def get_ancestors_chain(self, person: Person) -> list[Person]:
        """
        Get chain of ancestors (father's line only, traditional Chinese style)
        Returns list from immediate father to earliest known ancestor
        """
        ancestors = []
        current = person
        
        while current and current.father_id:
            father = await self.get_person(current.father_id)
            if father:
                ancestors.append(father)
                current = father
            else:
                break
        
        return ancestors
    
    async def get_spouses(self, person: Person) -> list[dict]:
        """
        Get all spouses with relation info
        
        Returns list of dicts with:
        - spouse: Person object
        - relation_type: type of relation
        - order: sort order
        """
        if person.gender == 'M':
            # Get all wives
            stmt = select(SpouseRelation).where(
                SpouseRelation.husband_id == person.id
            ).order_by(SpouseRelation.sort_order)
            result = await self.db.execute(stmt)
            relations = result.scalars().all()
            
            spouses = []
            for relation in relations:
                wife = await self.get_person(relation.wife_id)
                if wife:
                    spouses.append({
                        'spouse': wife,
                        'relation_type': relation.relation_type,
                        'order': relation.sort_order
                    })
            return spouses
            
        else:
            # Get husband
            stmt = select(SpouseRelation).where(
                SpouseRelation.wife_id == person.id
            )
            result = await self.db.execute(stmt)
            relations = result.scalars().all()
            
            spouses = []
            for relation in relations:
                husband = await self.get_person(relation.husband_id)
                if husband:
                    spouses.append({
                        'spouse': husband,
                        'relation_type': relation.relation_type,
                        'order': relation.sort_order
                    })
            return spouses
    
    async def get_parents(self, person: Person) -> dict:
        """Get parents of a person"""
        parents = {}
        
        if person.father_id:
            father = await self.get_person(person.father_id)
            if father:
                parents['father'] = father
        
        if person.mother_id:
            mother = await self.get_person(person.mother_id)
            if mother:
                parents['mother'] = mother
        
        return parents
    
    async def get_generation_title(self, generation_id: int) -> str:
        """Get traditional Chinese title for a generation"""
        stmt = select(Generation).where(Generation.id == generation_id)
        result = await self.db.execute(stmt)
        generation = result.scalar_one_or_none()
        
        if not generation:
            return f"第{generation_id}世"
        
        number = generation.number
        
        if number == 1:
            title = "始祖"
        elif number == 2:
            title = "二世祖"
        elif number == 3:
            title = "三世祖"
        elif number <= 9:
            title = f"{number}世祖"
        else:
            title = f"第{number}世"
        
        if generation.is_spouse:
            title += "（配）"
        
        return title
    
    async def get_family_members(self, person: Person) -> dict:
        """
        Get all family members for a person
        
        Returns dict with:
        - parents: list
        - spouses: list
        - children: list
        - siblings: list
        """
        parents_dict = await self.get_parents(person)
        parents = []
        if 'father' in parents_dict:
            parents.append(parents_dict['father'])
        if 'mother' in parents_dict:
            parents.append(parents_dict['mother'])
        
        spouses_data = await self.get_spouses(person)
        spouses = [s['spouse'] for s in spouses_data]
        
        children = await self.get_all_children(person)
        siblings = await self.get_siblings(person)
        
        return {
            'parents': parents,
            'spouses': spouses,
            'children': children,
            'siblings': siblings
        }
    
    async def add_spouse_relation(
        self,
        husband_id: UUID,
        wife_id: UUID,
        relation_type: str = "marriage",
        sort_order: int = 1
    ) -> SpouseRelation:
        """Create a new spouse relation"""
        relation = SpouseRelation(
            husband_id=husband_id,
            wife_id=wife_id,
            relation_type=relation_type,
            sort_order=sort_order
        )
        self.db.add(relation)
        await self.db.commit()
        await self.db.refresh(relation)
        return relation
    
    async def remove_spouse_relation(self, relation_id: UUID) -> bool:
        """Remove a spouse relation"""
        stmt = select(SpouseRelation).where(SpouseRelation.id == relation_id)
        result = await self.db.execute(stmt)
        relation = result.scalar_one_or_none()
        
        if relation:
            await self.db.delete(relation)
            await self.db.commit()
            return True
        return False
