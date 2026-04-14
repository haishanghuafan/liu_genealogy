"""
Excel data import service for bulk importing genealogy data
"""
import io
from typing import Optional
from uuid import UUID

import pandas as pd
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tenant import Person, Generation, Branch, SpouseRelation


class ExcelImportService:
    """Service for importing genealogy data from Excel files"""
    
    def __init__(self, db: AsyncSession, tenant_slug: str):
        self.db = db
        self.tenant_slug = tenant_slug
        self.errors = []
        self.success_count = 0
    
    async def import_from_excel(self, file_content: bytes) -> dict:
        """
        Import genealogy data from Excel file
        
        Expected columns:
        - name (required): 姓名
        - gender (required): 性别 (M/F)
        - generation_number (optional): 世代编号
        - branch_name (optional): 支系名称
        - father_name (optional): 父亲姓名
        - mother_name (optional): 母亲姓名
        - courtesy_name (optional): 字
        - art_name (optional): 号
        - birth_year (optional): 出生年份
        - death_year (optional): 逝世年份
        - birth_place (optional): 出生地
        - biography (optional): 生平简介
        - sort_order (optional): 排序
        
        Returns:
        {
            "success": bool,
            "imported_count": int,
            "errors": list,
            "details": list
        }
        """
        try:
            # Read Excel file
            df = pd.read_excel(io.BytesIO(file_content))
            
            # Validate required columns
            required_columns = ['name', 'gender']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                return {
                    "success": False,
                    "error": f"缺少必需列：{', '.join(missing_columns)}"
                }
            
            # Process rows
            results = []
            
            for index, row in df.iterrows():
                try:
                    person_data = await self._process_row(row)
                    results.append({
                        "row": index + 2,  # Excel row number (1-indexed + header)
                        "name": row.get('name', 'Unknown'),
                        "success": True,
                        "person_id": str(person_data.id) if person_data else None
                    })
                    self.success_count += 1
                except Exception as e:
                    error_msg = f"第 {index + 2} 行：{str(e)}"
                    self.errors.append(error_msg)
                    results.append({
                        "row": index + 2,
                        "name": row.get('name', 'Unknown'),
                        "success": False,
                        "error": str(e)
                    })
            
            return {
                "success": len(self.errors) == 0,
                "imported_count": self.success_count,
                "error_count": len(self.errors),
                "errors": self.errors,
                "details": results
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"文件读取失败：{str(e)}"
            }
    
    async def _process_row(self, row: pd.Series) -> Optional[Person]:
        """Process a single row and create/update person"""
        
        # Validate gender
        gender = row.get('gender', 'M').strip().upper()
        if gender not in ['M', 'F']:
            raise ValueError(f"性别必须为 M 或 F，当前值：{gender}")
        
        # Get or create generation
        generation = None
        gen_number = row.get('generation_number')
        if pd.notna(gen_number):
            generation = await self._get_or_create_generation(int(gen_number))
        
        # Get or create branch
        branch = None
        branch_name = row.get('branch_name')
        if pd.notna(branch_name) and str(branch_name).strip():
            branch = await self._get_or_create_branch(str(branch_name).strip())
        
        # Get parents
        father = None
        mother = None
        
        father_name = row.get('father_name')
        if pd.notna(father_name) and str(father_name).strip():
            father = await self._get_person_by_name(str(father_name).strip(), 'M')
        
        mother_name = row.get('mother_name')
        if pd.notna(mother_name) and str(mother_name).strip():
            mother = await self._get_person_by_name(str(mother_name).strip(), 'F')
        
        # Create or update person
        person = await self._get_or_create_person(
            name=str(row['name']).strip(),
            gender=gender,
            generation=generation,
            branch=branch,
            father=father,
            mother=mother,
            courtesy_name=row.get('courtesy_name'),
            art_name=row.get('art_name'),
            birth_year=row.get('birth_year'),
            death_year=row.get('death_year'),
            birth_place=row.get('birth_place'),
            biography=row.get('biography'),
            sort_order=row.get('sort_order')
        )
        
        return person
    
    async def _get_or_create_generation(self, number: int):
        """Get or create generation by number"""
        from sqlalchemy import select
        
        stmt = select(Generation).where(
            Generation.number == number,
            Generation.is_spouse == False
        )
        result = await self.db.execute(stmt)
        generation = result.scalar_one_or_none()
        
        if not generation:
            generation = Generation(
                number=number,
                is_spouse=False,
                title=f"第{number}代"
            )
            self.db.add(generation)
            await self.db.flush()
        
        return generation
    
    async def _get_or_create_branch(self, name: str):
        """Get or create branch by name"""
        from sqlalchemy import select
        
        stmt = select(Branch).where(Branch.name == name)
        result = await self.db.execute(stmt)
        branch = result.scalar_one_or_none()
        
        if not branch:
            branch = Branch(name=name)
            self.db.add(branch)
            await self.db.flush()
        
        return branch
    
    async def _get_person_by_name(self, name: str, gender: str):
        """Get person by name and gender"""
        from sqlalchemy import select
        
        stmt = select(Person).where(
            Person.name == name,
            Person.gender == gender
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def _get_or_create_person(
        self,
        name: str,
        gender: str,
        generation=None,
        branch=None,
        father=None,
        mother=None,
        **kwargs
    ) -> Person:
        """Get or create person by name and gender"""
        from sqlalchemy import select
        
        # Try to find existing person
        stmt = select(Person).where(
            Person.name == name,
            Person.gender == gender
        )
        result = await self.db.execute(stmt)
        person = result.scalar_one_or_none()
        
        if person:
            # Update existing person
            for field, value in kwargs.items():
                if hasattr(person, field) and pd.notna(value):
                    setattr(person, field, value)
            
            if generation:
                person.generation_id = generation.id
            if branch:
                person.branch_id = branch.id
            if father:
                person.father_id = father.id
            if mother:
                person.mother_id = mother.id
                
        else:
            # Create new person
            person_data = {
                'name': name,
                'gender': gender,
            }
            
            if generation:
                person_data['generation_id'] = generation.id
            if branch:
                person_data['branch_id'] = branch.id
            if father:
                person_data['father_id'] = father.id
            if mother:
                person_data['mother_id'] = mother.id
            
            # Add optional fields
            for field, value in kwargs.items():
                if hasattr(Person, field) and pd.notna(value):
                    if field in ['birth_year', 'death_year', 'sort_order']:
                        person_data[field] = int(value)
                    else:
                        person_data[field] = str(value)
            
            person = Person(**person_data)
            self.db.add(person)
            await self.db.flush()
        
        return person
