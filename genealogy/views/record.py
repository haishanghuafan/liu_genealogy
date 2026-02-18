"""
刘氏乾正公族谱 - 记录视图
"""
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django import forms
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from ..models import GenealogyRecord, Person


class GenealogyRecordListView(ListView):
    """族谱记录列表"""
    model = GenealogyRecord
    template_name = 'genealogy/record_list.html'
    context_object_name = 'records'
    paginate_by = 20
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class GenealogyRecordDetailView(DetailView):
    """族谱记录详情"""
    model = GenealogyRecord
    template_name = 'genealogy/record_detail.html'
    context_object_name = 'record'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        record = self.object
        context['related_persons'] = record.related_persons.all()
        return context


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


class RecordCreateView(LoginRequiredMixin, CreateView):
    model = GenealogyRecord
    form_class = RecordForm
    template_name = 'genealogy/form.html'
    
    def get_success_url(self):
        return reverse_lazy('genealogy:record_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = '创建记录'
        context['submit_text'] = '创建'
        return context
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['related_persons'].queryset = Person.objects.all()
        return form


class RecordUpdateView(LoginRequiredMixin, UpdateView):
    model = GenealogyRecord
    form_class = RecordForm
    template_name = 'genealogy/form.html'
    
    def get_success_url(self):
        return reverse_lazy('genealogy:record_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = '编辑记录'
        context['submit_text'] = '保存修改'
        return context
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['related_persons'].queryset = Person.objects.all()
        return form
