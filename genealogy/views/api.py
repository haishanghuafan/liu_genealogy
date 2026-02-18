"""
刘氏乾正公族谱 - API视图
"""
from django.shortcuts import get_object_or_404
from django.views.generic import View
from django.http import JsonResponse
from ..models import Person, SpouseRelation


class FamilyTreeAPIView(View):
    """家族树API - 返回ECharts格式的数据"""
    
    def get(self, request, pk):
        person = get_object_or_404(Person, pk=pk)
        
        def build_tree_node(p, include_parents=True, include_children=True):
            """构建树节点"""
            node = {
                'id': p.id,
                'name': p.name,
                'gender': p.gender,
                'generation': p.generation.number if p.generation else 0,
                'url': p.get_absolute_url(),
                'children': []
            }
            
            if p.gender == 'M':
                spouse_relations = SpouseRelation.objects.filter(husband=p)
                for relation in spouse_relations:
                    spouse_node = {
                        'id': relation.wife.id,
                        'name': relation.wife.name,
                        'gender': relation.wife.gender,
                        'generation': relation.wife.generation.number if relation.wife.generation else 0,
                        'url': relation.wife.get_absolute_url(),
                        'relation_type': relation.relation_type,
                        'children': []
                    }
                    children = Person.objects.filter(father=p, mother=relation.wife)
                    for child in children:
                        spouse_node['children'].append(build_tree_node(child, include_parents=False, include_children=True))
                    node['children'].append(spouse_node)
                
                unknown_mother_children = Person.objects.filter(father=p, mother__isnull=True)
                for child in unknown_mother_children:
                    node['children'].append(build_tree_node(child, include_parents=False, include_children=True))
            else:
                spouse_relations = SpouseRelation.objects.filter(wife=p)
                for relation in spouse_relations:
                    spouse_node = {
                        'id': relation.husband.id,
                        'name': relation.husband.name,
                        'gender': relation.husband.gender,
                        'generation': relation.husband.generation.number if relation.husband.generation else 0,
                        'url': relation.husband.get_absolute_url(),
                        'relation_type': relation.relation_type,
                        'children': []
                    }
                    children = Person.objects.filter(mother=p, father=relation.husband)
                    for child in children:
                        spouse_node['children'].append(build_tree_node(child, include_parents=False, include_children=True))
                    node['children'].append(spouse_node)
                
                unknown_father_children = Person.objects.filter(mother=p, father__isnull=True)
                for child in unknown_father_children:
                    node['children'].append(build_tree_node(child, include_parents=False, include_children=True))
            
            return node
        
        root = build_tree_node(person)
        
        def build_ancestor_tree(p):
            ancestors = []
            current = p
            while current.father:
                ancestors.append({
                    'id': current.father.id,
                    'name': current.father.name,
                    'gender': current.father.gender,
                    'generation': current.father.generation.number if current.father.generation else 0,
                    'url': current.father.get_absolute_url()
                })
                current = current.father
            return list(reversed(ancestors))
        
        return JsonResponse({
            'person': {
                'id': person.id,
                'name': person.name,
                'gender': person.gender,
                'generation': person.generation.number if person.generation else 0,
            },
            'tree': root,
            'ancestors': build_ancestor_tree(person)
        })


def get_generations(request):
    """获取世代选项（用于AJAX请求）"""
    from ..models import Generation
    
    is_outsider = request.GET.get('is_outsider', 'false') == 'true'
    
    generations = Generation.objects.filter(is_spouse=is_outsider).order_by('number', 'is_spouse')
    
    generations_data = []
    for gen in generations:
        generations_data.append({
            'id': gen.id,
            'name': str(gen)
        })
    
    return JsonResponse({'generations': generations_data})
