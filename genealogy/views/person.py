"""
刘氏乾正公族谱 - 人物视图
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, View
from django import forms
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from ..models import Person, Generation, Branch, SpouseRelation
from ..permissions import PersonOwnerMixin


class PersonListView(ListView):
    """人物列表"""
    model = Person
    template_name = 'genealogy/person_list.html'
    context_object_name = 'persons'
    paginate_by = 50
    
    def get_queryset(self):
        queryset = Person.objects.select_related('generation', 'father', 'branch')
        
        generation = self.request.GET.get('generation')
        if generation:
            queryset = queryset.filter(generation__number=generation)
        
        branch = self.request.GET.get('branch')
        if branch:
            queryset = queryset.filter(branch_id=branch)
        
        gender = self.request.GET.get('gender')
        if gender:
            queryset = queryset.filter(gender=gender)
        
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(courtesy_name__icontains=search) |
                Q(art_name__icontains=search) |
                Q(alias__icontains=search)
            )
        
        return queryset.order_by('generation__number', 'order', 'id')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['generations'] = Generation.objects.filter(is_spouse=False).all()
        context['branches'] = Branch.objects.all()
        context['search_query'] = self.request.GET.get('search', '')
        return context


class PersonDetailView(DetailView):
    """人物详情"""
    model = Person
    template_name = 'genealogy/person_detail.html'
    context_object_name = 'person'
    
    def get_queryset(self):
        return Person.objects.select_related(
            'generation', 'father', 'mother', 'branch'
        ).prefetch_related(
            'spouses',
            'husband_relations',
            'wife_relations',
            'children_as_father',
            'children_as_mother',
            'images',
            'videos'
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        person = self.object
        
        if person.gender == 'M':
            spouse_relations = SpouseRelation.objects.filter(husband=person)
        else:
            spouse_relations = SpouseRelation.objects.filter(wife=person)
        context['spouse_relations'] = spouse_relations
        
        children = person.get_all_children()
        context['children'] = children
        
        children_by_spouse = []
        if person.gender == 'M':
            for relation in spouse_relations:
                spouse_children = []
                for child in children:
                    if child.mother == relation.wife:
                        spouse_children.append(child)
                children_by_spouse.append({
                    'spouse': relation.wife,
                    'children': spouse_children,
                    'relation_type': relation.relation_type,
                    'order': relation.order
                })
            unknown_mother_children = [child for child in children if not child.mother]
            if unknown_mother_children:
                children_by_spouse.append({
                    'spouse': None,
                    'children': unknown_mother_children,
                    'relation_type': None,
                    'order': 999
                })
        else:
            for relation in spouse_relations:
                spouse_children = []
                for child in children:
                    if child.father == relation.husband:
                        spouse_children.append(child)
                children_by_spouse.append({
                    'spouse': relation.husband,
                    'children': spouse_children,
                    'relation_type': relation.relation_type,
                    'order': relation.order
                })
            unknown_father_children = [child for child in children if not child.father]
            if unknown_father_children:
                children_by_spouse.append({
                    'spouse': None,
                    'children': unknown_father_children,
                    'relation_type': None,
                    'order': 999
                })
        context['children_by_spouse'] = children_by_spouse
        
        siblings = person.get_siblings()
        context['siblings'] = siblings
        
        ancestors = person.get_ancestors_chain()
        context['ancestors'] = ancestors
        
        family_members = person.get_family_members()
        context['family_members'] = family_members
        
        context['generation_depth'] = person.get_generation_depth()
        if hasattr(person, 'generation') and person.generation:
            context['generation_title'] = person.generation.get_generation_title()
        
        return context


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
        from django.db import IntegrityError
        
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


class PersonCreateView(LoginRequiredMixin, CreateView):
    """创建人物视图"""
    model = Person
    form_class = PersonForm
    template_name = 'genealogy/person_form.html'
    
    def get_success_url(self):
        return reverse_lazy('genealogy:person_detail', kwargs={'pk': self.object.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = '创建人物'
        context['submit_text'] = '创建'
        context['children'] = []
        context['spouses'] = []
        return context
    
    def form_valid(self, form):
        response = super().form_valid(form)
        form.save_child(form.instance, self.request.user)
        form.save_spouse(form.instance, self.request.user)
        return response


class PersonUpdateView(LoginRequiredMixin, PersonOwnerMixin, UpdateView):
    """编辑人物视图"""
    model = Person
    form_class = PersonForm
    template_name = 'genealogy/person_form.html'
    
    def get_success_url(self):
        return reverse_lazy('genealogy:person_detail', kwargs={'pk': self.object.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = '编辑人物'
        context['submit_text'] = '保存修改'
        
        children = set()
        children.update(self.object.children_as_father.all())
        children.update(self.object.children_as_mother.all())
        context['children'] = sorted(children, key=lambda x: (x.order, x.id))
        
        spouses = []
        if self.object.gender == 'M':
            for rel in self.object.husband_relations.all():
                spouses.append({'person': rel.wife, 'relation_type': rel.get_relation_type_display(), 'relation': rel})
        else:
            for rel in self.object.wife_relations.all():
                spouses.append({'person': rel.husband, 'relation_type': rel.get_relation_type_display(), 'relation': rel})
        context['spouses'] = spouses
        
        return context
    
    def form_valid(self, form):
        form.save_child(form.instance, self.request.user)
        form.save_spouse(form.instance, self.request.user)
        response = super().form_valid(form)
        return response


class PersonEditView(PersonOwnerMixin, View):
    """用户编辑自己关联的人物信息"""
    template_name = 'genealogy/person_edit.html'
    
    def get(self, request, pk):
        person = get_object_or_404(Person, pk=pk)
        return render(request, self.template_name, {
            'person': person,
        })
    
    def post(self, request, pk):
        person = get_object_or_404(Person, pk=pk)
        return redirect('genealogy:person_detail', pk=pk)
