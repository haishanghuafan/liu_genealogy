"""
族谱数据导入脚本
根据两份族谱文档整理的数据
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'liu_genealogy.settings')
django.setup()

from genealogy.models import Generation, Branch, Person, SpouseRelation


def create_generations():
    """创建世代"""
    print("创建世代...")
    for i in range(1, 20):
        Generation.objects.get_or_create(
            number=i,
            defaults={'name': f'第{i}世'}
        )
    print(f"创建了 {Generation.objects.count()} 个世代")


def create_branches():
    """创建支系"""
    print("创建支系...")
    branches_data = [
        {
            'name': '法海公支系',
            'location': '梅县凤坑、田福村',
            'description': '法海公后裔，主要居住在梅县凤坑、田福村、井下、崩田角、大角山等地'
        },
        {
            'name': '淮海公支系',
            'location': '平远东石',
            'description': '淮海公后裔，主要居住在平远东石明洋陂下、河头象牙村、热柘下黄地等地'
        },
        {
            'name': '得成公支系',
            'location': '梅县水南坝',
            'description': '得成公后裔，原住梅县水南坝，后裔分迁长沙、扶贵、丙村、潮州、广西、江西等地'
        },
        {
            'name': '沧海公支系',
            'location': '平远茅寮坪',
            'description': '沧海公后裔，分平远茅寮坪、小柘下黄塘开基'
        },
        {
            'name': '千一公支系',
            'location': '蕉岭县凤岭',
            'description': '千一公后裔，分蕉岭县凤岭开基'
        },
        {
            'name': '满海公支系',
            'location': '平远各地',
            'description': '满海公后裔，外迁平远热柘小柘开基，西山下田心、茅坪石角陂、坝头樟演等地'
        },
    ]
    
    for data in branches_data:
        Branch.objects.get_or_create(
            name=data['name'],
            defaults={
                'location': data['location'],
                'description': data['description']
            }
        )
    print(f"创建了 {Branch.objects.count()} 个支系")


def create_first_ancestor():
    """创建一世祖乾正公"""
    print("创建一世祖...")
    gen1 = Generation.objects.get(number=1)
    
    # 创建乾正公
    qianzheng, _ = Person.objects.get_or_create(
        name='乾正公',
        defaults={
            'generation': gen1,
            'courtesy_name': '法教',
            'art_name': '三十七郎、文昌',
            'gender': 'M',
            'biography': '法教公号乾正、三十七郎，又字文昌。祖于元朝徙居嘉应州水南坝，后住凤坑，殁于凤坑，葬于凤坑。',
            'burial_place': '凤坑土名乌坑里张屋后',
            'burial_fengshui': '乌鸦落洋形',
            'burial_direction': '辛山乙向',
            'order': 1
        }
    )
    
    # 创建陈氏妣
    chen, _ = Person.objects.get_or_create(
        name='陈氏',
        defaults={
            'generation': gen1,
            'gender': 'F',
            'biography': '乾正公妣陈氏',
            'burial_place': '平远小柘天弓岌',
            'burial_fengshui': '眼镜形（又名天平对针形）',
            'order': 2
        }
    )
    
    # 创建配偶关系
    SpouseRelation.objects.get_or_create(
        husband=qianzheng,
        wife=chen,
        defaults={'order': 1}
    )
    
    print(f"一世祖: {qianzheng.name}")
    return qianzheng


def create_second_generation(qianzheng):
    """创建二世祖（六子）"""
    print("创建二世祖（六子）...")
    gen2 = Generation.objects.get(number=2)
    
    # 获取支系
    fahai_branch = Branch.objects.get(name='法海公支系')
    huaihai_branch = Branch.objects.get(name='淮海公支系')
    decheng_branch = Branch.objects.get(name='得成公支系')
    canghai_branch = Branch.objects.get(name='沧海公支系')
    qianyi_branch = Branch.objects.get(name='千一公支系')
    manhai_branch = Branch.objects.get(name='满海公支系')
    
    sons_data = [
        {
            'name': '法海公',
            'branch': fahai_branch,
            'spouse': '徐氏七娘',
            'spouse2': '徐氏八娘',
            'order': 1
        },
        {
            'name': '淮海公',
            'branch': huaihai_branch,
            'spouse': '宋氏',
            'order': 2
        },
        {
            'name': '得成公',
            'branch': decheng_branch,
            'spouse': '罗氏',
            'order': 3
        },
        {
            'name': '沧海公',
            'branch': canghai_branch,
            'spouse': '凌氏',
            'order': 4
        },
        {
            'name': '千一公',
            'branch': qianyi_branch,
            'spouse': '陈氏',
            'order': 5
        },
        {
            'name': '满海公',
            'branch': manhai_branch,
            'spouse': '朱氏',
            'spouse2': '陈氏',
            'order': 6
        },
    ]
    
    for data in sons_data:
        # 创建儿子
        son, _ = Person.objects.get_or_create(
            name=data['name'],
            defaults={
                'generation': gen2,
                'gender': 'M',
                'father': qianzheng,
                'branch': data['branch'],
                'order': data['order']
            }
        )
        
        # 创建配偶
        if 'spouse' in data:
            spouse, _ = Person.objects.get_or_create(
                name=data['spouse'],
                defaults={
                    'generation': gen2,
                    'gender': 'F',
                    'order': data['order'] + 100
                }
            )
            SpouseRelation.objects.get_or_create(
                husband=son,
                wife=spouse,
                defaults={'order': 1}
            )
        
        if 'spouse2' in data:
            spouse2, _ = Person.objects.get_or_create(
                name=data['spouse2'],
                defaults={
                    'generation': gen2,
                    'gender': 'F',
                    'order': data['order'] + 200
                }
            )
            SpouseRelation.objects.get_or_create(
                husband=son,
                wife=spouse2,
                defaults={'order': 2}
            )
        
        print(f"  创建: {son.name}")
    
    print(f"二世祖共 {Person.objects.filter(generation=gen2, gender='M').count()} 人")


def create_third_generation():
    """创建三世祖"""
    print("创建三世祖...")
    gen3 = Generation.objects.get(number=3)
    gen2 = Generation.objects.get(number=2)
    
    # 法海公的儿子们
    fahai = Person.objects.get(name='法海公', generation=gen2)
    
    # 法聪公
    facong, _ = Person.objects.get_or_create(
        name='法聪公',
        defaults={
            'generation': gen3,
            'gender': 'M',
            'father': fahai,
            'branch': fahai.branch,
            'order': 1
        }
    )
    
    # 创建法聪公的配偶姚氏
    yao, _ = Person.objects.get_or_create(
        name='姚氏',
        defaults={
            'generation': gen3,
            'gender': 'F',
            'order': 101
        }
    )
    SpouseRelation.objects.get_or_create(
        husband=facong,
        wife=yao,
        defaults={'order': 1}
    )
    
    # 淮海公的儿子们
    huaihai = Person.objects.get(name='淮海公', generation=gen2)
    
    # 千一郎公
    qianyilang, _ = Person.objects.get_or_create(
        name='千一郎公',
        defaults={
            'generation': gen3,
            'gender': 'M',
            'father': huaihai,
            'branch': huaihai.branch,
            'order': 2
        }
    )
    
    # 刘荫公
    liuyin, _ = Person.objects.get_or_create(
        name='刘荫公',
        defaults={
            'generation': gen3,
            'gender': 'M',
            'father': huaihai,
            'branch': huaihai.branch,
            'biography': '景泰进士，刑部主事',
            'order': 3
        }
    )
    
    # 得成公的儿子们
    decheng = Person.objects.get(name='得成公', generation=gen2)
    
    # 文通公
    wentong, _ = Person.objects.get_or_create(
        name='文通公',
        defaults={
            'generation': gen3,
            'gender': 'M',
            'father': decheng,
            'branch': decheng.branch,
            'order': 4
        }
    )
    
    # 文聪公
    wencong, _ = Person.objects.get_or_create(
        name='文聪公',
        defaults={
            'generation': gen3,
            'gender': 'M',
            'father': decheng,
            'branch': decheng.branch,
            'order': 5
        }
    )
    
    # 千一公的儿子
    qianyi = Person.objects.get(name='千一公', generation=gen2)
    
    # 永通公
    yongtong, _ = Person.objects.get_or_create(
        name='永通公',
        defaults={
            'generation': gen3,
            'gender': 'M',
            'father': qianyi,
            'branch': qianyi.branch,
            'descendants_location': '后裔分迁蕉岭县凤岭开基',
            'order': 6
        }
    )
    
    # 满海公的儿子们
    manhai = Person.objects.get(name='满海公', generation=gen2)
    
    # 永端公、永正公、永敬公、文英公、文援公
    manhai_sons = [
        {'name': '永端公', 'order': 7},
        {'name': '永正公', 'order': 8},
        {'name': '永敬公', 'order': 9},
        {'name': '文英公', 'order': 10},
        {'name': '文援公', 'order': 11},
    ]
    
    for data in manhai_sons:
        Person.objects.get_or_create(
            name=data['name'],
            defaults={
                'generation': gen3,
                'gender': 'M',
                'father': manhai,
                'branch': manhai.branch,
                'order': data['order']
            }
        )
    
    print(f"三世祖共 {Person.objects.filter(generation=gen3, gender='M').count()} 人")


def create_fourth_generation():
    """创建四世祖 - 法聪公的儿子们"""
    print("创建四世祖...")
    gen4 = Generation.objects.get(number=4)
    gen3 = Generation.objects.get(number=3)
    
    facong = Person.objects.get(name='法聪公', generation=gen3)
    
    # 法聪公的五个儿子
    sons = [
        {'name': '忡瑛公（法行）', 'order': 1},
        {'name': '忡瑞公', 'order': 2},
        {'name': '忡瑄公（法瑄）', 'order': 3},
        {'name': '忡渊公', 'order': 4},
        {'name': '忡璵公', 'order': 5},
    ]
    
    for data in sons:
        Person.objects.get_or_create(
            name=data['name'],
            defaults={
                'generation': gen4,
                'gender': 'M',
                'father': facong,
                'branch': facong.branch,
                'order': data['order']
            }
        )
    
    print(f"四世祖共 {Person.objects.filter(generation=gen4, gender='M').count()} 人")


def create_fifth_generation():
    """创建五世祖 - 法行公的儿子们"""
    print("创建五世祖...")
    gen5 = Generation.objects.get(number=5)
    gen4 = Generation.objects.get(number=4)
    
    # 法行公的儿子们
    faxing = Person.objects.get(name='忡瑛公（法行）', generation=gen4)
    
    # 法宽公、法猷公
    sons = [
        {'name': '法宽公', 'order': 1},
        {'name': '法猷公', 'order': 2},
    ]
    
    for data in sons:
        Person.objects.get_or_create(
            name=data['name'],
            defaults={
                'generation': gen5,
                'gender': 'M',
                'father': faxing,
                'branch': faxing.branch,
                'order': data['order']
            }
        )
    
    print(f"五世祖共 {Person.objects.filter(generation=gen5, gender='M').count()} 人")


def create_sixth_generation():
    """创建六世祖 - 法宽公的儿子们"""
    print("创建六世祖...")
    gen6 = Generation.objects.get(number=6)
    gen5 = Generation.objects.get(number=5)
    
    # 法宽公的儿子们
    fakuan = Person.objects.get(name='法宽公', generation=gen5)
    
    # 刘辉公、德立公
    sons = [
        {
            'name': '刘辉公',
            'order': 1,
            'descendants_location': '后裔安居梅西田福杨梅树下乾正公祖屋'
        },
        {
            'name': '德立公（刘鸾）',
            'order': 2,
            'descendants_location': '后裔汝永公迁住金山月梅草塘等外地'
        },
    ]
    
    for data in sons:
        Person.objects.get_or_create(
            name=data['name'],
            defaults={
                'generation': gen6,
                'gender': 'M',
                'father': fakuan,
                'branch': fakuan.branch,
                'descendants_location': data['descendants_location'],
                'order': data['order']
            }
        )
    
    # 法猷公的儿子们
    fayou = Person.objects.get(name='法猷公', generation=gen5)
    
    # 创建法猷公的八个儿子
    fayou_sons = [
        '刘琮公', '刘珍公（玲）', '刘璋公（法高）', '刘瑄公',
        '刘璉公（法璉）', '刘玘公', '刘瑀公（法瑀）', '刘珦公（法珦）'
    ]
    
    for i, name in enumerate(fayou_sons, start=3):
        Person.objects.get_or_create(
            name=name,
            defaults={
                'generation': gen6,
                'gender': 'M',
                'father': fayou,
                'branch': fayou.branch,
                'order': i
            }
        )
    
    print(f"六世祖共 {Person.objects.filter(generation=gen6, gender='M').count()} 人")


def create_seventh_generation():
    """创建七世祖"""
    print("创建七世祖...")
    gen7 = Generation.objects.get(number=7)
    gen6 = Generation.objects.get(number=6)
    
    # 德立公的儿子 - 承创公
    deli = Person.objects.get(name='德立公（刘鸾）', generation=gen6)
    
    Person.objects.get_or_create(
        name='承创公',
        defaults={
            'generation': gen7,
            'gender': 'M',
            'father': deli,
            'branch': deli.branch,
            'descendants_location': '后裔汝永公迁住金山月梅草塘等外地',
            'order': 1
        }
    )
    
    print(f"七世祖共 {Person.objects.filter(generation=gen7, gender='M').count()} 人")


def update_branch_founders():
    """更新支系开基祖"""
    print("更新支系开基祖...")
    
    gen2 = Generation.objects.get(number=2)
    
    # 更新各支系的开基祖
    branch_founder_mapping = {
        '法海公支系': '法海公',
        '淮海公支系': '淮海公',
        '得成公支系': '得成公',
        '沧海公支系': '沧海公',
        '千一公支系': '千一公',
        '满海公支系': '满海公',
    }
    
    for branch_name, founder_name in branch_founder_mapping.items():
        try:
            branch = Branch.objects.get(name=branch_name)
            founder = Person.objects.get(name=founder_name, generation=gen2)
            branch.founder = founder
            branch.save()
            print(f"  {branch_name} -> {founder_name}")
        except (Branch.DoesNotExist, Person.DoesNotExist):
            print(f"  跳过: {branch_name}")


def main():
    """主函数"""
    print("=" * 50)
    print("开始导入族谱数据")
    print("=" * 50)
    
    # 清空现有数据
    print("\n清空现有数据...")
    SpouseRelation.objects.all().delete()
    Person.objects.all().delete()
    Branch.objects.all().delete()
    Generation.objects.all().delete()
    
    # 创建数据
    create_generations()
    create_branches()
    qianzheng = create_first_ancestor()
    create_second_generation(qianzheng)
    create_third_generation()
    create_fourth_generation()
    create_fifth_generation()
    create_sixth_generation()
    create_seventh_generation()
    update_branch_founders()
    
    print("\n" + "=" * 50)
    print("数据导入完成！")
    print("=" * 50)
    print(f"\n统计:")
    print(f"  世代: {Generation.objects.count()}")
    print(f"  支系: {Branch.objects.count()}")
    print(f"  人物: {Person.objects.count()}")
    print(f"  配偶关系: {SpouseRelation.objects.count()}")


if __name__ == '__main__':
    main()
