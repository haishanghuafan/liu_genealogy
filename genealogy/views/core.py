"""
刘氏乾正公族谱 - 核心视图
"""
from django.shortcuts import render, redirect
from django.views.generic import TemplateView, View
from django.contrib.auth import logout
from django.db.models import Q
from ..models import Person, Generation, Branch


class HomeView(TemplateView):
    """首页"""
    template_name = 'genealogy/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_persons'] = Person.objects.count()
        context['total_generations'] = Generation.objects.filter(is_spouse=False).count()
        context['total_branches'] = Branch.objects.count()
        context['first_ancestor'] = Person.objects.filter(generation__number=1).first()
        context['recent_persons'] = Person.objects.order_by('-updated_at')[:10]
        return context


class GenealogyTreeView(TemplateView):
    """世系图页面"""
    template_name = 'genealogy/tree.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        generations = Generation.objects.filter(is_spouse=False).prefetch_related('persons').all()
        context['generations'] = generations
        
        first_ancestor = Person.objects.filter(generation__number=1).first()
        context['first_ancestor'] = first_ancestor
        
        branches = Branch.objects.all()
        context['branches'] = branches
        
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


def logout_view(request):
    """自定义登出视图，支持GET请求"""
    logout(request)
    return redirect('genealogy:home')
