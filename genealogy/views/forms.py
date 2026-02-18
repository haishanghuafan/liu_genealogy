"""
刘氏乾正公族谱 - 表单
"""
import django.forms as forms
from django.db import IntegrityError
from django.urls import reverse_lazy
from ..models import Person, Generation, Branch, SpouseRelation, GenealogyRecord


class PersonForm(forms.ModelForm):
    """人物表单"""
    new_children = forms.CharField(
        required=False, 
        label='新增子女',
        widget=forms.Textarea(attrs={
            'class': 'form-control', 
            'rows': 3,
            'placeholder': '每行一个姓名，格式：姓名,性别（用英文逗号，如：张三,男 或 李四,女）'
        })
    )
    new_spouse_name = forms.CharField(
        max_length=100, 
        required=False, 
        label='新增配偶姓名',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '输入姓名添加新配偶'})
    )
    new_spouse_gender = forms.ChoiceField(
        choices=Person.GENDER_CHOICES,
        required=False,
        label='新增配偶性别',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    new_spouse_relation_type = forms.ChoiceField(
        choices=SpouseRelation.RELATION_TYPE_CHOICES,
        required=False,
        label='关系类型',
        initial='marriage',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    class Meta:
        model = Person
        fields = [
            'name', 'courtesy_name', 'art_name', 'alias', 'generation_char',
            'gender', 'is_outsider', 'generation', 'father', 'mother', 'branch',
            'birth_year', 'death_year', 'birth_place',
            'burial_place', 'burial_fengshui', 'burial_direction',
            'biography', 'achievements', 'descendants_location', 'notes', 'avatar'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'courtesy_name': forms.TextInput(attrs={'class': 'form-control'}),
            'art_name': forms.TextInput(attrs={'class': 'form-control'}),
            'alias': forms.TextInput(attrs={'class': 'form-control'}),
            'generation_char': forms.TextInput(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'is_outsider': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'generation': forms.Select(attrs={'class': 'form-select'}),
            'father': forms.Select(attrs={'class': 'form-select'}),
            'mother': forms.Select(attrs={'class': 'form-select'}),
            'branch': forms.Select(attrs={'class': 'form-select'}),
            'birth_year': forms.NumberInput(attrs={'class': 'form-control'}),
            'death_year': forms.NumberInput(attrs={'class': 'form-control'}),
            'birth_place': forms.TextInput(attrs={'class': 'form-control'}),
            'burial_place': forms.TextInput(attrs={'class': 'form-control'}),
            'burial_fengshui': forms.TextInput(attrs={'class': 'form-control'}),
            'burial_direction': forms.TextInput(attrs={'class': 'form-control'}),
            'biography': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'achievements': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'descendants_location': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'avatar': forms.FileInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['father'].queryset = Person.objects.filter(gender='M')
        self.fields['mother'].queryset = Person.objects.filter(gender='F')
        self.fields['generation'].queryset = Generation.objects.all()
        self.fields['branch'].queryset = Branch.objects.all()
    
    def clean(self):
        cleaned_data = super().clean()
        new_children = cleaned_data.get('new_children')
        
        children_list = []
        if new_children:
            for line in new_children.strip().split('\n'):
                line = line.strip()
                if not line:
                    continue
                
                line = line.replace('，', ',')
                
                if ',' in line:
                    parts = line.split(',', 1)
                    name = parts[0].strip()
                    gender_str = parts[1].strip().upper() if len(parts) > 1 else ''
                    if gender_str in ['男', 'M']:
                        gender = 'M'
                    elif gender_str in ['女', 'F']:
                        gender = 'F'
                    else:
                        raise forms.ValidationError(f'性别"{parts[1].strip()}"无效，请使用"男/M"或"女/F"')
                else:
                    name = line.strip()
                    gender = None
                
                if not name:
                    continue
                
                if not gender:
                    raise forms.ValidationError(f'姓名"{name}"缺少性别信息，请使用"姓名,性别"格式（用英文或中文逗号）')
                
                if Person.objects.filter(name=name, gender=gender).exists():
                    gender_desc = "男性" if gender == 'M' else "女性"
                    raise forms.ValidationError(f'姓名"{name}"的{gender_desc}已存在，请查找并编辑现有人物')
                children_list.append({'name': name, 'gender': gender})
        
        cleaned_data['children_list'] = children_list
        return cleaned_data
    
    def save_child(self, parent, user):
        children_list = self.cleaned_data.get('children_list', [])
        
        if not children_list:
            return []
        
        next_generation = None
        
        if parent.generation:
            next_generation = Generation.objects.filter(
                number=parent.generation.number + 1
            ).first()
            
            if not next_generation:
                try:
                    next_generation = Generation.objects.create(
                        number=parent.generation.number + 1,
                        name=f'第{parent.generation.number + 1}世'
                    )
                except IntegrityError:
                    next_generation = Generation.objects.filter(
                        number=parent.generation.number + 1
                    ).first()
                except Exception:
                    pass
        
        if not next_generation:
            max_gen = Generation.objects.order_by('-number').first()
            next_gen_number = (max_gen.number + 1) if max_gen else 1
            next_generation = Generation.objects.create(
                number=next_gen_number,
                name=f'第{next_gen_number}世'
            )
        
        created_children = []
        for child_data in children_list:
            name = child_data.get('name')
            gender = child_data.get('gender')
            
            if not name or not gender:
                continue
            
            child = Person.objects.create(
                name=name,
                gender=gender,
                generation=next_generation,
                branch=parent.branch,
                father=parent if parent.gender == 'M' else None,
                mother=parent if parent.gender == 'F' else None,
                created_by=user
            )
            
            if parent.gender == 'M':
                parent.children_as_father.add(child)
            else:
                parent.children_as_mother.add(child)
            
            created_children.append(child)
        
        return created_children
    
    def save_spouse(self, person, user):
        new_spouse_name = self.cleaned_data.get('new_spouse_name')
        new_spouse_gender = self.cleaned_data.get('new_spouse_gender')
        new_spouse_relation_type = self.cleaned_data.get('new_spouse_relation_type')
        
        if not new_spouse_name or not new_spouse_gender:
            return None
        
        spouse_gender_opposite = 'F' if person.gender == 'M' else 'M'
        
        if new_spouse_gender != spouse_gender_opposite:
            return None
        
        existing_spouse = Person.objects.filter(name=new_spouse_name, gender=new_spouse_gender).first()
        
        if existing_spouse:
            spouse = existing_spouse
        else:
            spouse = Person.objects.create(
                name=new_spouse_name,
                gender=new_spouse_gender,
                generation=person.generation,
                branch=person.branch,
                is_outsider=True,
                created_by=user
            )
        
        relation_type = new_spouse_relation_type or 'marriage'
        
        if person.gender == 'M':
            SpouseRelation.objects.get_or_create(
                husband=person,
                wife=spouse,
                defaults={'relation_type': relation_type}
            )
        else:
            SpouseRelation.objects.get_or_create(
                husband=spouse,
                wife=person,
                defaults={'relation_type': relation_type}
            )
        
        return spouse


class GenerationForm(forms.ModelForm):
    class Meta:
        model = Generation
        fields = ['number', 'is_spouse', 'name', 'description']
        widgets = {
            'number': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_spouse': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class BranchForm(forms.ModelForm):
    class Meta:
        model = Branch
        fields = ['name', 'founder', 'description', 'location']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'founder': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
        }


class RecordForm(forms.ModelForm):
    class Meta:
        model = GenealogyRecord
        fields = ['title', 'content', 'source', 'source_image', 'page_number', 'related_persons', 'notes']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'source': forms.TextInput(attrs={'class': 'form-control'}),
            'source_image': forms.FileInput(attrs={'class': 'form-control'}),
            'page_number': forms.TextInput(attrs={'class': 'form-control'}),
            'related_persons': forms.CheckboxSelectMultiple(),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
