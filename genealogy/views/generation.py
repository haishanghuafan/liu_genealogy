"""
刘氏乾正公族谱 - 世代视图
"""
from django.views.generic import ListView, CreateView, UpdateView
from django import forms
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from ..models import Generation


class GenerationListView(ListView):
    """世代列表"""
    model = Generation
    template_name = 'genealogy/generation_list.html'
    context_object_name = 'generations'
    
    def get_queryset(self):
        return Generation.objects.filter(is_spouse=False).distinct()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        for generation in context['generations']:
            generation.person_count = generation.persons.count()
        return context


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


class GenerationCreateView(LoginRequiredMixin, CreateView):
    model = Generation
    form_class = GenerationForm
    template_name = 'genealogy/form.html'
    
    def get_success_url(self):
        return reverse_lazy('genealogy:generation_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = '创建世代'
        context['submit_text'] = '创建'
        return context


class GenerationUpdateView(LoginRequiredMixin, UpdateView):
    model = Generation
    form_class = GenerationForm
    template_name = 'genealogy/form.html'
    
    def get_success_url(self):
        return reverse_lazy('genealogy:generation_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = '编辑世代'
        context['submit_text'] = '保存修改'
        return context
