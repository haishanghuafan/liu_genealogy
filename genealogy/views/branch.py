"""
刘氏乾正公族谱 - 支系视图
"""
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from ..models import Branch, Person
from .forms import BranchForm


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


class BranchCreateView(LoginRequiredMixin, CreateView):
    model = Branch
    form_class = BranchForm
    template_name = 'genealogy/form.html'
    
    def get_success_url(self):
        return reverse_lazy('genealogy:branch_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = '创建支系'
        context['submit_text'] = '创建'
        return context
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['founder'].queryset = Person.objects.all()
        return form


class BranchUpdateView(LoginRequiredMixin, UpdateView):
    model = Branch
    form_class = BranchForm
    template_name = 'genealogy/form.html'
    
    def get_success_url(self):
        return reverse_lazy('genealogy:branch_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = '编辑支系'
        context['submit_text'] = '保存修改'
        return context
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['founder'].queryset = Person.objects.all()
        return form
