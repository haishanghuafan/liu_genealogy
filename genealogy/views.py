"""
刘氏乾正公族谱 - 视图
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import (
    TemplateView,
    ListView,
    DetailView,
    View,
)
from django.contrib.auth import login, authenticate
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Q
from django.core.paginator import Paginator
from .models import Person, Generation, Branch, SpouseRelation, UserProfile


class HomeView(TemplateView):
    """首页"""
    template_name = 'genealogy/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_persons'] = Person.objects.count()
        context['total_generations'] = Generation.objects.count()
        context['total_branches'] = Branch.objects.count()
        context['first_ancestor'] = Person.objects.filter(generation__number=1).first()
        context['recent_persons'] = Person.objects.order_by('-updated_at')[:10]
        return context


class GenealogyTreeView(TemplateView):
    """世系图页面"""
    template_name = 'genealogy/tree.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 获取所有世代
        generations = Generation.objects.prefetch_related('persons').all()
        context['generations'] = generations
        
        # 获取始祖
        first_ancestor = Person.objects.filter(generation__number=1).first()
        context['first_ancestor'] = first_ancestor
        
        # 获取主要支系
        branches = Branch.objects.all()
        context['branches'] = branches
        
        return context


class PersonListView(ListView):
    """人物列表"""
    model = Person
    template_name = 'genealogy/person_list.html'
    context_object_name = 'persons'
    paginate_by = 50
    
    def get_queryset(self):
        queryset = Person.objects.select_related('generation', 'father', 'branch')
        
        # 按世代筛选
        generation = self.request.GET.get('generation')
        if generation:
            queryset = queryset.filter(generation__number=generation)
        
        # 按支系筛选
        branch = self.request.GET.get('branch')
        if branch:
            queryset = queryset.filter(branch_id=branch)
        
        # 按性别筛选
        gender = self.request.GET.get('gender')
        if gender:
            queryset = queryset.filter(gender=gender)
        
        # 搜索
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
        context['generations'] = Generation.objects.all()
        context['branches'] = Branch.objects.all()
        context['search_query'] = self.request.GET.get('search', '')
        return context


class PersonDetailView(DetailView):
    """人物详情"""
    model = Person
    template_name = 'genealogy/person_detail.html'
    context_object_name = 'person'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        person = self.object
        
        # 获取配偶
        if person.gender == 'M':
            spouse_relations = SpouseRelation.objects.filter(husband=person)
        else:
            spouse_relations = SpouseRelation.objects.filter(wife=person)
        context['spouse_relations'] = spouse_relations
        
        # 获取子女
        if person.gender == 'M':
            children = Person.objects.filter(father=person)
        else:
            children = Person.objects.filter(mother=person)
        context['children'] = children
        
        # 获取兄弟姐妹
        siblings = []
        if person.father:
            siblings = Person.objects.filter(
                father=person.father
            ).exclude(pk=person.pk)
        context['siblings'] = siblings
        
        # 祖先路径
        ancestors = []
        current = person
        while current.father:
            ancestors.append(current.father)
            current = current.father
        context['ancestors'] = reversed(ancestors)
        
        return context


class BranchListView(ListView):
    """支系列表"""
    model = Branch
    template_name = 'genealogy/branch_list.html'
    context_object_name = 'branches'


class BranchDetailView(DetailView):
    """支系详情"""
    model = Branch
    template_name = 'genealogy/branch_detail.html'
    context_object_name = 'branch'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        branch = self.object
        context['members'] = Person.objects.filter(
            branch=branch
        ).select_related('generation').order_by('generation__number')
        return context


class GenerationListView(ListView):
    """世代列表"""
    model = Generation
    template_name = 'genealogy/generation_list.html'
    context_object_name = 'generations'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        for generation in context['generations']:
            generation.person_count = generation.persons.count()
        return context


class SearchView(View):
    """搜索页面"""
    template_name = 'genealogy/search.html'
    
    def get(self, request):
        query = request.GET.get('q', '')
        results = []
        
        if query:
            results = Person.objects.filter(
                Q(name__icontains=query) |
                Q(courtesy_name__icontains=query) |
                Q(art_name__icontains=query) |
                Q(alias__icontains=query) |
                Q(biography__icontains=query) |
                Q(achievements__icontains=query)
            ).select_related('generation', 'branch')[:50]
        
        return render(request, self.template_name, {
            'query': query,
            'results': results,
        })


class RegisterView(View):
    """用户注册"""
    template_name = 'genealogy/register.html'
    
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('genealogy:home')
        form = UserCreationForm()
        return render(request, self.template_name, {'form': form})
    
    def post(self, request):
        if request.user.is_authenticated:
            return redirect('genealogy:home')
        
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # 创建用户资料
            UserProfile.objects.create(user=user)
            # 自动登录
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
            return redirect('genealogy:home')
        
        return render(request, self.template_name, {'form': form})


class ProfileView(LoginRequiredMixin, View):
    """用户资料"""
    template_name = 'genealogy/profile.html'
    
    def get(self, request):
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        return render(request, self.template_name, {
            'profile': profile,
            'user': request.user,
        })
