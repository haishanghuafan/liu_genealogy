#!/usr/bin/env python3
"""
族谱数据导出脚本 - 将数据库数据导出到Excel表格
"""
import os
import django
import pandas as pd
from openpyxl import Workbook

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'liu_genealogy.settings')
django.setup()

from genealogy.models import Generation, Branch, Person, SpouseRelation

def export_generations():
    """导出世代数据"""
    print("导出世代数据...")
    try:
        generations = Generation.objects.all()
        data = []
        for gen in generations:
            data.append({
                '世代数': gen.number,
                '是否为配偶世代': '是' if gen.is_spouse else '否',
                '世代名称': gen.name,
                '描述': gen.description
            })
        return pd.DataFrame(data)
    except Exception as e:
        print(f"❌ 导出世代数据失败: {e}")
        return pd.DataFrame()

def export_branches():
    """导出支系数据"""
    print("导出支系数据...")
    try:
        branches = Branch.objects.all()
        data = []
        for branch in branches:
            founder_name = branch.founder.name if branch.founder else ''
            data.append({
                '支系名称': branch.name,
                '开基祖': founder_name,
                '描述': branch.description,
                '分布地区': branch.location
            })
        return pd.DataFrame(data)
    except Exception as e:
        print(f"❌ 导出支系数据失败: {e}")
        return pd.DataFrame()

def export_persons():
    """导出人物数据"""
    print("导出人物数据...")
    try:
        persons = Person.objects.all()
        data = []
        for person in persons:
            father_name = person.father.name if person.father else ''
            mother_name = person.mother.name if person.mother else ''
            generation_name = person.generation.name if person.generation else ''
            branch_name = person.branch.name if person.branch else ''
            gender = '男' if person.gender == 'M' else '女'
            
            data.append({
                '姓名': person.name,
                '字': person.courtesy_name,
                '号': person.art_name,
                '别名': person.alias,
                '辈份字': person.generation_char,
                '性别': gender,
                '是否为外族配偶': '是' if person.is_outsider else '否',
                '世代数': person.generation.number if person.generation else '',
                '世代名称': generation_name,
                '父亲姓名': father_name,
                '母亲姓名': mother_name,
                '所属支系': branch_name,
                '出生年份': person.birth_year,
                '逝世年份': person.death_year,
                '出生地': person.birth_place,
                '葬地': person.burial_place,
                '墓形/风水': person.burial_fengshui,
                '坐向': person.burial_direction,
                '生平简介': person.biography,
                '主要事迹': person.achievements,
                '后裔分布': person.descendants_location,
                '备注': person.notes,
                '排序': person.order,
                '账号状态': person.account_status,
                '创建时间': person.created_at.replace(tzinfo=None) if person.created_at else '',
                '更新时间': person.updated_at.replace(tzinfo=None) if person.updated_at else ''
            })
        return pd.DataFrame(data)
    except Exception as e:
        print(f"❌ 导出人物数据失败: {e}")
        return pd.DataFrame()

def export_spouse_relations():
    """导出配偶关系数据"""
    print("导出配偶关系数据...")
    try:
        relations = SpouseRelation.objects.all()
        data = []
        for relation in relations:
            data.append({
                '丈夫姓名': relation.husband.name,
                '妻子姓名': relation.wife.name,
                '关系类型': relation.get_relation_type_display(),
                '配偶来源信息': relation.source_info,
                '排序（第几任）': relation.order
            })
        return pd.DataFrame(data)
    except Exception as e:
        print(f"❌ 导出配偶关系数据失败: {e}")
        return pd.DataFrame()

def export_data_to_excel(excel_file):
    """导出所有数据到Excel文件"""
    print(f"导出数据到Excel文件: {excel_file}")
    
    # 创建Excel文件
    with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
        # 导出世代数据
        generations_df = export_generations()
        if not generations_df.empty:
            generations_df.to_excel(writer, sheet_name='世代', index=False)
        
        # 导出支系数据
        branches_df = export_branches()
        if not branches_df.empty:
            branches_df.to_excel(writer, sheet_name='支系', index=False)
        
        # 导出人物数据
        persons_df = export_persons()
        if not persons_df.empty:
            persons_df.to_excel(writer, sheet_name='人物', index=False)
        
        # 导出配偶关系数据
        relations_df = export_spouse_relations()
        if not relations_df.empty:
            relations_df.to_excel(writer, sheet_name='配偶关系', index=False)
    
    print(f"✅ 成功导出数据到 {excel_file}")

def main():
    """主函数"""
    print("=" * 50)
    print("族谱数据导出工具")
    print("=" * 50)
    
    excel_file = 'genealogy_data.xlsx'
    export_data_to_excel(excel_file)
    
    print("\n" + "=" * 50)
    print("操作完成！")
    print("=" * 50)


if __name__ == '__main__':
    main()
