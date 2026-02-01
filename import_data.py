#!/usr/bin/env python3
"""
族谱数据导入脚本 - 支持从Excel表格导入数据
"""
import os
import django
import pandas as pd

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'liu_genealogy.settings')
django.setup()

from genealogy.models import Generation, Branch, Person, SpouseRelation

def import_generations_from_excel(excel_file):
    """从Excel导入世代数据"""
    print("导入世代数据...")
    try:
        df = pd.read_excel(excel_file, sheet_name='世代')
        for _, row in df.iterrows():
            number = int(row['世代数'])
            name = str(row['世代名称']) if pd.notna(row['世代名称']) else f'第{number}世'
            generation_char = str(row['辈份字']) if pd.notna(row['辈份字']) else ''
            
            Generation.objects.get_or_create(
                number=number,
                defaults={
                    'name': name,
                    'generation_char': generation_char
                }
            )
        print(f"✅ 成功导入 {Generation.objects.count()} 个世代")
    except Exception as e:
        print(f"❌ 导入世代数据失败: {e}")

def import_persons_from_excel(excel_file):
    """从Excel导入人物数据"""
    print("导入人物数据...")
    try:
        df = pd.read_excel(excel_file, sheet_name='人物')
        person_mapping = {}
        
        # 先创建所有人物，不设置关系
        for _, row in df.iterrows():
            name = str(row['姓名']) if pd.notna(row['姓名']) else ''
            if not name:
                continue
            
            courtesy_name = str(row['字']) if pd.notna(row['字']) else ''
            art_name = str(row['号']) if pd.notna(row['号']) else ''
            alias = str(row['别名']) if pd.notna(row['别名']) else ''
            gender = str(row['性别']) if pd.notna(row['性别']) else 'M'
            gender = 'M' if gender == '男' else 'F'
            
            generation_number = int(row['世代数']) if pd.notna(row['世代数']) else 1
            generation = Generation.objects.get_or_create(number=generation_number)[0]
            
            birth_year = int(row['出生年份']) if pd.notna(row['出生年份']) else None
            death_year = int(row['逝世年份']) if pd.notna(row['逝世年份']) else None
            birth_place = str(row['出生地']) if pd.notna(row['出生地']) else ''
            branch_name = str(row['所属支系']) if pd.notna(row['所属支系']) else ''
            biography = str(row['生平简介']) if pd.notna(row['生平简介']) else ''
            achievements = str(row['主要事迹']) if pd.notna(row['主要事迹']) else ''
            descendants_location = str(row['后裔分布']) if pd.notna(row['后裔分布']) else ''
            burial_place = str(row['葬地']) if pd.notna(row['葬地']) else ''
            burial_fengshui = str(row['墓形/风水']) if pd.notna(row['墓形/风水']) else ''
            burial_direction = str(row['坐向']) if pd.notna(row['坐向']) else ''
            notes = str(row['备注']) if pd.notna(row['备注']) else ''
            order = int(row['排序']) if pd.notna(row['排序']) else 0
            
            # 获取或创建支系
            branch = None
            if branch_name:
                branch, _ = Branch.objects.get_or_create(
                    name=branch_name,
                    defaults={'description': f'{branch_name}支系'}
                )
            
            # 创建人物
            person, _ = Person.objects.get_or_create(
                name=name,
                defaults={
                    'generation': generation,
                    'courtesy_name': courtesy_name,
                    'art_name': art_name,
                    'alias': alias,
                    'gender': gender,
                    'branch': branch,
                    'birth_year': birth_year,
                    'death_year': death_year,
                    'birth_place': birth_place,
                    'biography': biography,
                    'achievements': achievements,
                    'descendants_location': descendants_location,
                    'burial_place': burial_place,
                    'burial_fengshui': burial_fengshui,
                    'burial_direction': burial_direction,
                    'notes': notes,
                    'order': order
                }
            )
            person_mapping[name] = person
        
        # 然后设置父子关系
        print("设置人物关系...")
        df = pd.read_excel(excel_file, sheet_name='人物')
        for _, row in df.iterrows():
            name = str(row['姓名']) if pd.notna(row['姓名']) else ''
            if not name or name not in person_mapping:
                continue
            
            person = person_mapping[name]
            
            # 设置父亲
            father_name = str(row['父亲姓名']) if pd.notna(row['父亲姓名']) else ''
            if father_name and father_name in person_mapping:
                person.father = person_mapping[father_name]
            
            # 设置母亲
            mother_name = str(row['母亲姓名']) if pd.notna(row['母亲姓名']) else ''
            if mother_name and mother_name in person_mapping:
                person.mother = person_mapping[mother_name]
            
            person.save()
        
        print(f"✅ 成功导入 {Person.objects.count()} 个人物")
    except Exception as e:
        print(f"❌ 导入人物数据失败: {e}")

def import_spouse_relations_from_excel(excel_file):
    """从Excel导入配偶关系数据"""
    print("导入配偶关系数据...")
    try:
        df = pd.read_excel(excel_file, sheet_name='配偶关系')
        person_mapping = {}
        
        # 构建人物映射
        for person in Person.objects.all():
            person_mapping[person.name] = person
        
        # 创建配偶关系
        for _, row in df.iterrows():
            husband_name = str(row['丈夫姓名']) if pd.notna(row['丈夫姓名']) else ''
            wife_name = str(row['妻子姓名']) if pd.notna(row['妻子姓名']) else ''
            order = int(row['排序']) if pd.notna(row['排序']) else 1
            
            if husband_name and wife_name and husband_name in person_mapping and wife_name in person_mapping:
                husband = person_mapping[husband_name]
                wife = person_mapping[wife_name]
                
                SpouseRelation.objects.get_or_create(
                    husband=husband,
                    wife=wife,
                    defaults={'order': order}
                )
        
        print(f"✅ 成功导入 {SpouseRelation.objects.count()} 个配偶关系")
    except Exception as e:
        print(f"❌ 导入配偶关系数据失败: {e}")

def import_data_from_excel(excel_file):
    """从Excel导入所有数据"""
    print(f"从Excel文件导入数据: {excel_file}")
    
    # 清空现有数据
    print("清空现有数据...")
    SpouseRelation.objects.all().delete()
    Person.objects.all().delete()
    Branch.objects.all().delete()
    Generation.objects.all().delete()
    
    # 导入数据
    import_generations_from_excel(excel_file)
    import_persons_from_excel(excel_file)
    import_spouse_relations_from_excel(excel_file)
    
    print("\n数据导入完成！")
    print(f"统计:")
    print(f"  世代: {Generation.objects.count()}")
    print(f"  支系: {Branch.objects.count()}")
    print(f"  人物: {Person.objects.count()}")
    print(f"  配偶关系: {SpouseRelation.objects.count()}")

def create_default_data():
    """创建默认数据（当没有Excel文件时使用）"""
    print("创建默认数据...")
    
    # 创建世代
    for i in range(1, 21):
        Generation.objects.get_or_create(
            number=i,
            defaults={'name': f'第{i}世'}
        )
    
    # 创建支系
    branches_data = [
        {'name': '法海公支系', 'location': '梅县凤坑、田福村', 'description': '法海公后裔'},  
        {'name': '淮海公支系', 'location': '平远东石', 'description': '淮海公后裔'},
        {'name': '得成公支系', 'location': '梅县水南坝', 'description': '得成公后裔'},
        {'name': '沧海公支系', 'location': '平远茅寮坪', 'description': '沧海公后裔'},
        {'name': '千一公支系', 'location': '蕉岭县凤岭', 'description': '千一公后裔'},
        {'name': '满海公支系', 'location': '平远各地', 'description': '满海公后裔'},
    ]
    
    for data in branches_data:
        Branch.objects.get_or_create(
            name=data['name'],
            defaults={'location': data['location'], 'description': data['description']}
        )
    
    print("默认数据创建完成！")

def main():
    """主函数"""
    print("=" * 50)
    print("族谱数据导入工具")
    print("=" * 50)
    
    excel_file = 'genealogy_data.xlsx'
    
    if os.path.exists(excel_file):
        print(f"找到Excel文件: {excel_file}")
        import_data_from_excel(excel_file)
    else:
        print(f"未找到Excel文件: {excel_file}")
        print("请先填写 genealogy_template.xlsx 并保存为 genealogy_data.xlsx")
        create_default_data()
    
    print("\n" + "=" * 50)
    print("操作完成！")
    print("=" * 50)


if __name__ == '__main__':
    main()
