"""
刘氏乾正公族谱 - 管理视图
"""
from django.shortcuts import render
from django.views.generic import TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from ..models import Person, Generation, Branch, GenealogyRecord, UserProfile


class ManagementView(LoginRequiredMixin, TemplateView):
    """数据管理首页"""
    template_name = 'genealogy/management.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_persons'] = Person.objects.count()
        context['total_generations'] = Generation.objects.filter(is_spouse=False).count()
        context['total_branches'] = Branch.objects.count()
        context['total_records'] = GenealogyRecord.objects.count()
        return context


class UploadMediaView(LoginRequiredMixin, View):
    """上传资料视图，允许用户上传与自己关联人物相关的图片和视频"""
    template_name = 'genealogy/upload_media.html'
    
    def get(self, request):
        related_person = None
        if hasattr(request.user, 'related_person'):
            related_person = request.user.related_person
        else:
            try:
                profile = UserProfile.objects.get(user=request.user)
                if profile.related_person:
                    related_person = profile.related_person
            except:
                pass
        
        if not related_person:
            return render(request, self.template_name, {
                'error': '您还没有关联任何人物，请联系管理员为您设置。'
            })
        
        return render(request, self.template_name, {
            'related_person': related_person
        })
    
    def post(self, request):
        related_person = None
        if hasattr(request.user, 'related_person'):
            related_person = request.user.related_person
        else:
            try:
                profile = UserProfile.objects.get(user=request.user)
                if profile.related_person:
                    related_person = profile.related_person
            except:
                pass
        
        if not related_person:
            return render(request, self.template_name, {
                'error': '您还没有关联任何人物，请联系管理员为您设置。'
            })
        
        media_type = request.POST.get('media_type')
        title = request.POST.get('title')
        description = request.POST.get('description')
        file = request.FILES.get('file')
        
        if not media_type or not title or not file:
            return render(request, self.template_name, {
                'related_person': related_person,
                'error': '请填写完整的表单信息。'
            })
        
        try:
            if media_type == 'image':
                from ..models import PersonImage
                PersonImage.objects.create(
                    person=related_person,
                    image=file,
                    title=title,
                    description=description
                )
            elif media_type == 'video':
                from ..models import PersonVideo
                PersonVideo.objects.create(
                    person=related_person,
                    video=file,
                    title=title,
                    description=description
                )
            success = '资料上传成功！'
        except Exception as e:
            success = None
            error = f'上传失败：{str(e)}'
        
        return render(request, self.template_name, {
            'related_person': related_person,
            'success': success,
            'error': error
        })
