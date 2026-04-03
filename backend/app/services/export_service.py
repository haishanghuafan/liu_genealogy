"""
Export service - generate Excel/PDF exports
"""
from datetime import datetime
from io import BytesIO
from typing import List, Optional
from uuid import UUID

import pandas as pd
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tenant import Person, Generation, Branch, SpouseRelation


class ExportService:
    """Service for exporting genealogy data"""
    
    @staticmethod
    async def export_persons_excel(
        db: AsyncSession,
        tenant_slug: str,
        generation_filter: Optional[int] = None,
        branch_filter: Optional[str] = None,
    ) -> BytesIO:
        """Export persons to Excel file"""
        
        # Build query
        query = select(Person)
        
        if generation_filter:
            query = query.where(Person.generation_id == generation_filter)
        
        if branch_filter:
            query = query.where(Person.branch_id == UUID(branch_filter))
        
        query = query.order_by(Person.generation_id, Person.sort_order, Person.id)
        
        result = await db.execute(query)
        persons = result.scalars().all()
        
        # Get generations and branches for lookup
        gen_result = await db.execute(select(Generation))
        generations = {g.id: g for g in gen_result.scalars().all()}
        
        branch_result = await db.execute(select(Branch))
        branches = {b.id: b for b in branch_result.scalars().all()}
        
        # Build data for export
        data = []
        for p in persons:
            gen = generations.get(p.generation_id)
            branch = branches.get(p.branch_id)
            
            # Get father and mother names
            father_name = None
            mother_name = None
            
            data.append({
                "姓名": p.name,
                "字": p.courtesy_name or "",
                "号": p.art_name or "",
                "别名": p.alias or "",
                "辈分字": p.generation_char or "",
                "性别": "男" if p.gender == "M" else "女",
                "世代": f"第{gen.number}世" if gen else "",
                "支系": branch.name if branch else "",
                "出生年": p.birth_year or "",
                "逝世年": p.death_year or "",
                "出生地": p.birth_place or "",
                "安葬地": p.burial_place or "",
                "生平简介": p.biography or "",
                "成就荣誉": p.achievements or "",
                "后人分布": p.descendants_location or "",
                "备注": p.notes or "",
            })
        
        # Create DataFrame
        df = pd.DataFrame(data)
        
        # Export to Excel
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='人物列表', index=False)
            
            # Auto-adjust column widths
            worksheet = writer.sheets['人物列表']
            for idx, col in enumerate(df.columns):
                max_len = max(df[col].astype(str).str.len().max(), len(col)) + 2
                worksheet.column_dimensions[chr(65 + idx) if idx < 26 else f"A{chr(65 + idx - 26)}"].width = min(max_len, 50)
        
        output.seek(0)
        return output
    
    @staticmethod
    async def export_generations_excel(db: AsyncSession) -> BytesIO:
        """Export generations to Excel"""
        result = await db.execute(select(Generation).order_by(Generation.number))
        generations = result.scalars().all()
        
        data = [{
            "世代数": g.number,
            "世代名称": g.name,
            "描述": g.description or "",
        } for g in generations]
        
        df = pd.DataFrame(data)
        
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='世代列表', index=False)
        
        output.seek(0)
        return output
    
    @staticmethod
    async def export_spouse_relations_excel(db: AsyncSession) -> BytesIO:
        """Export spouse relations to Excel"""
        result = await db.execute(select(SpouseRelation))
        relations = result.scalars().all()
        
        # Get all persons for name lookup
        persons_result = await db.execute(select(Person))
        persons = {str(p.id): p for p in persons_result.scalars().all()}
        
        relation_type_names = {
            "marriage": "婚姻（正室）",
            "concubine": "妾室",
            "adopted": "继配",
            "zhuazhui": "招赘",
            "first": "一房",
            "second": "二房",
            "third": "三房",
            "fourth": "四房",
            "fifth": "五房",
        }
        
        data = []
        for r in relations:
            husband = persons.get(str(r.husband_id))
            wife = persons.get(str(r.wife_id))
            
            data.append({
                "丈夫姓名": husband.name if husband else "",
                "妻子姓名": wife.name if wife else "",
                "关系类型": relation_type_names.get(r.relation_type, r.relation_type),
                "来源信息": r.source_info or "",
                "排序": r.sort_order,
            })
        
        df = pd.DataFrame(data)
        
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='配偶关系', index=False)
        
        output.seek(0)
        return output
    
    @staticmethod
    async def export_full_excel(db: AsyncSession, tenant_slug: str) -> BytesIO:
        """Export full genealogy data to a single Excel file with multiple sheets"""
        
        output = BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # Sheet 1: Generations
            gen_output = await ExportService.export_generations_excel(db)
            gen_df = pd.read_excel(gen_output, sheet_name='世代列表')
            gen_df.to_excel(writer, sheet_name='世代', index=False)
            
            # Sheet 2: Persons
            persons_output = await ExportService.export_persons_excel(db, tenant_slug)
            persons_df = pd.read_excel(persons_output, sheet_name='人物列表')
            persons_df.to_excel(writer, sheet_name='人物', index=False)
            
            # Sheet 3: Spouse Relations
            relations_output = await ExportService.export_spouse_relations_excel(db)
            relations_df = pd.read_excel(relations_output, sheet_name='配偶关系')
            relations_df.to_excel(writer, sheet_name='配偶关系', index=False)
        
        output.seek(0)
        return output


export_service = ExportService()
