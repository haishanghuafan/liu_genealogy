"""
Excel data import service for bulk importing genealogy data
"""
import io
from typing import Optional
from uuid import UUID

import pandas as pd
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tenant import Person, Generation, Branch, SpouseRelation


class ExcelImportService:
    """Service for importing genealogy data from Excel files"""

    def __init__(self, db: AsyncSession, tenant_slug: str):
        self.db = db
        self.tenant_slug = tenant_slug
        self.errors = []
        self.success_count = 0
        self.person_map = {}

    async def import_from_excel(self, file_content: bytes) -> dict:
        """
        Import genealogy data from Excel file

        Supports two template formats:
        1. Index-based (序号型): Uses '人物序号', '父亲序号', '母亲序号' for relationships
        2. Name-based (姓名型): Uses 'father_name', 'mother_name' for relationships

        Returns:
        {
            "success": bool,
            "imported_count": int,
            "errors": list,
            "details": list
        }
        """
        try:
            df = pd.read_excel(io.BytesIO(file_content))
            
            normalized_columns = {
                '人物序号': 'person_index',
                '姓名': 'name',
                '性别': 'gender',
                '是否为外族配偶': 'is_outsider',
                '世代数': 'generation_number',
                '世代名称': 'generation_name',
                '父亲序号': 'father_index',
                '母亲序号': 'mother_index',
                '配偶序号列表': 'spouse_indexes',
                '字': 'courtesy_name',
                '号': 'art_name',
                '别名': 'alias',
                '支系名称': 'branch_name',
                '支系世代名称': 'branch_generation_name',
                '辈分字': 'generation_char',
                '出生日期': 'birth_date',
                '逝世日期': 'death_year',
                '葬地（墓形/风水/坐向）': 'burial_place',
                '生平简介（人物事迹和后裔分布）': 'biography',
                '备注': 'notes',
                'name': 'name',
                'gender': 'gender',
                'generation_number': 'generation_number',
                'branch_name': 'branch_name',
                'father_name': 'father_name',
                'mother_name': 'mother_name',
                'courtesy_name': 'courtesy_name',
                'art_name': 'art_name',
                'birth_year': 'birth_year',
                'death_year': 'death_year',
                'birth_place': 'birth_place',
                'biography': 'biography',
                'sort_order': 'sort_order',
            }
            df.columns = [normalized_columns.get(col.strip(), col.strip()) for col in df.columns]

            required_columns = ['name', 'gender']
            missing_columns = [col for col in required_columns if col not in df.columns]

            if missing_columns:
                return {
                    "success": False,
                    "error": f"缺少必需列：{', '.join(missing_columns)}"
                }

            has_index = 'person_index' in df.columns
            results = []

            if has_index:
                results = await self._import_index_based(df)
            else:
                results = await self._import_name_based(df)

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

    async def _import_index_based(self, df: pd.DataFrame) -> list:
        """Import using index-based relationships (序号型模板)"""
        import logging
        logger = logging.getLogger(__name__)
        
        from sqlalchemy import func
        results = []
        
        logger.warning(f"Columns after normalization: {list(df.columns)}")
        logger.warning(f"First row data: {df.iloc[0].to_dict() if len(df) > 0 else 'empty'}")

        for idx, row in df.iterrows():
            try:
                person_index = int(row['person_index']) if pd.notna(row.get('person_index')) else None
                name = str(row['name']).strip()
                gender_raw = str(row.get('gender', 'M')).strip()
                gender = self._normalize_gender(gender_raw)

                generation_number = None
                if pd.notna(row.get('generation_number')):
                    try:
                        generation_number = int(row['generation_number'])
                    except:
                        pass

                generation = None
                if generation_number:
                    generation = await self._get_or_create_generation(generation_number)

                branch = None
                branch_name = row.get('branch_name')
                if pd.notna(branch_name) and str(branch_name).strip():
                    branch = await self._get_or_create_branch(str(branch_name).strip())

                birth_year = None
                if pd.notna(row.get('birth_date')):
                    birth_year = self._extract_year(row.get('birth_date'))
                elif pd.notna(row.get('birth_year')):
                    birth_year = self._extract_year(row.get('birth_year'))

                death_year = None
                if pd.notna(row.get('death_year')):
                    death_year = self._extract_year(row.get('death_year'))

                person = Person(
                    name=name,
                    gender=gender,
                    courtesy_name=str(row['courtesy_name']).strip() if pd.notna(row.get('courtesy_name')) else None,
                    art_name=str(row['art_name']).strip() if pd.notna(row.get('art_name')) else None,
                    alias=str(row['alias']).strip() if pd.notna(row.get('alias')) else None,
                    generation_id=generation.id if generation else None,
                    branch_id=branch.id if branch else None,
                    birth_year=birth_year,
                    death_year=death_year,
                    burial_place=str(row['burial_place']).strip() if pd.notna(row.get('burial_place')) else None,
                    biography=str(row['biography']).strip() if pd.notna(row.get('biography')) else None,
                    notes=str(row['notes']).strip() if pd.notna(row.get('notes')) else None,
                    is_outsider=bool(row.get('is_outsider') == '是'),
                )

                self.db.add(person)
                await self.db.flush()
                await self.db.refresh(person)

                self.person_map[person_index] = person

                results.append({
                    "row": idx + 2,
                    "name": name,
                    "success": True,
                    "person_id": str(person.id)
                })
                self.success_count += 1

            except Exception as e:
                error_msg = f"第 {idx + 2} 行：{str(e)}"
                self.errors.append(error_msg)
                results.append({
                    "row": idx + 2,
                    "name": row.get('name', 'Unknown'),
                    "success": False,
                    "error": str(e)
                })

        await self.db.flush()

        for idx, row in df.iterrows():
            try:
                person_index = int(row['person_index']) if pd.notna(row.get('person_index')) else None
                if person_index is None:
                    continue

                person = self.person_map.get(person_index)
                if person is None:
                    continue

                father_index = None
                if pd.notna(row.get('father_index')):
                    try:
                        father_index = int(row['father_index'])
                    except:
                        pass

                mother_index = None
                if pd.notna(row.get('mother_index')):
                    try:
                        mother_index = int(row['mother_index'])
                    except:
                        pass

                spouse_indexes_str = row.get('spouse_indexes')
                spouse_indexes = []
                if pd.notna(spouse_indexes_str):
                    spouse_indexes = []
                    for x in str(spouse_indexes_str).split(','):
                        x = x.strip()
                        if x:
                            try:
                                spouse_indexes.append(int(float(x)))
                            except:
                                pass

                if father_index and father_index in self.person_map:
                    person.father_id = self.person_map[father_index].id

                if mother_index and mother_index in self.person_map:
                    person.mother_id = self.person_map[mother_index].id

                if spouse_indexes:
                    for spouse_index in spouse_indexes:
                        if spouse_index in self.person_map:
                            spouse = self.person_map[spouse_index]
                            if person.gender == 'M' and spouse.gender == 'F':
                                spouse_rel = SpouseRelation(
                                    husband_id=person.id,
                                    wife_id=spouse.id
                                )
                                self.db.add(spouse_rel)
                            elif person.gender == 'F' and spouse.gender == 'M':
                                spouse_rel = SpouseRelation(
                                    husband_id=spouse.id,
                                    wife_id=person.id
                                )
                                self.db.add(spouse_rel)

            except Exception as e:
                self.errors.append(f"第 {idx + 2} 行关系建立失败：{str(e)}")

        await self.db.commit()
        return results

    async def _import_name_based(self, df: pd.DataFrame) -> list:
        """Import using name-based relationships (姓名型模板)"""
        results = []

        for idx, row in df.iterrows():
            try:
                gender_raw = str(row.get('gender', 'M')).strip()
                gender = self._normalize_gender(gender_raw)

                generation = None
                gen_number = row.get('generation_number')
                if pd.notna(gen_number):
                    generation = await self._get_or_create_generation(int(gen_number))

                branch = None
                branch_name = row.get('branch_name')
                if pd.notna(branch_name) and str(branch_name).strip():
                    branch = await self._get_or_create_branch(str(branch_name).strip())

                father = None
                father_name = row.get('father_name')
                if pd.notna(father_name) and str(father_name).strip():
                    father = await self._get_person_by_name(str(father_name).strip(), 'M')

                mother = None
                mother_name = row.get('mother_name')
                if pd.notna(mother_name) and str(mother_name).strip():
                    mother = await self._get_person_by_name(str(mother_name).strip(), 'F')

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

                results.append({
                    "row": idx + 2,
                    "name": row.get('name', 'Unknown'),
                    "success": True,
                    "person_id": str(person.id) if person else None
                })
                if person:
                    self.success_count += 1

            except Exception as e:
                error_msg = f"第 {idx + 2} 行：{str(e)}"
                self.errors.append(error_msg)
                results.append({
                    "row": idx + 2,
                    "name": row.get('name', 'Unknown'),
                    "success": False,
                    "error": str(e)
                })

        return results

    def _normalize_gender(self, gender_raw: str) -> str:
        """Normalize gender value to M or F"""
        gender_map = {'男': 'M', '女': 'F', 'male': 'M', 'female': 'F', 'M': 'M', 'F': 'F'}
        return gender_map.get(gender_raw, 'M' if gender_raw.upper() == 'M' else 'F')

    def _extract_year(self, value) -> Optional[int]:
        """Extract year from various date formats"""
        if pd.isna(value):
            return None
        try:
            val_str = str(value).strip()
            return int(float(val_str))
        except:
            return None

    async def _get_or_create_generation(self, number: int):
        """Get or create generation by number"""
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
                name=f"第{number}代"
            )
            self.db.add(generation)
            await self.db.flush()

        return generation

    async def _get_or_create_branch(self, name: str):
        """Get or create branch by name"""
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
        stmt = select(Person).where(
            Person.name == name,
            Person.gender == gender
        )
        result = await self.db.execute(stmt)
        person = result.scalar_one_or_none()

        if person:
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

    async def clear_all_data(self) -> dict:
        """
        Clear all genealogy data for the tenant
        Deletes in order: spouse_relations -> persons -> branches -> generations
        """
        try:
            await self.db.execute(delete(SpouseRelation))
            await self.db.execute(delete(Person))
            await self.db.execute(delete(Branch))
            await self.db.execute(delete(Generation))
            await self.db.commit()

            return {
                "success": True,
                "message": "已清空所有数据"
            }
        except Exception as e:
            await self.db.rollback()
            return {
                "success": False,
                "error": f"清空数据失败：{str(e)}"
            }

    async def replace_import(self, file_content: bytes) -> dict:
        """
        Replace all existing data with new import
        This will clear all existing persons, branches, and generations first,
        then import the new data from the Excel file.
        """
        import logging
        logger = logging.getLogger(__name__)
        
        logger.warning("Step 1: Clearing all data...")
        clear_result = await self.clear_all_data()
        if not clear_result["success"]:
            logger.error(f"Clear data failed: {clear_result}")
            return clear_result
        
        logger.warning("Step 2: Importing new data...")
        self.errors = []
        self.success_count = 0
        self.person_map = {}

        try:
            result = await self.import_from_excel(file_content)
            logger.warning(f"Import result: success={result.get('success')}, count={result.get('imported_count')}, errors={len(result.get('errors', []))}")
            return result
        except Exception as e:
            logger.error(f"Import exception: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": f"导入过程异常：{str(e)}"
            }
