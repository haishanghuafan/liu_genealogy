"""
刘氏乾正公族谱 - 认证视图
"""
from django.shortcuts import render, redirect
from django.views.generic import View
from django.contrib.auth import login, authenticate
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from ..models import Person, UserProfile


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
        related_person = None
        if hasattr(request.user, 'related_person'):
            related_person = request.user.related_person
        elif profile.related_person:
            related_person = profile.related_person
        
        return render(request, self.template_name, {
            'profile': profile,
            'user': request.user,
            'related_person': related_person,
        })


class MyFamilyView(LoginRequiredMixin, View):
    """我的家族视图，显示用户关联人物的家族树"""
    template_name = 'genealogy/my_family.html'
    
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
        
        ancestors = []
        descendants = []
        if related_person:
            current = related_person
            while current.father:
                ancestors.append(current.father)
                current = current.father
            ancestors.reverse()
            
            def get_descendants(person):
                kids = []
                if person.gender == 'M':
                    children = person.children_as_father.all()
                else:
                    children = person.children_as_mother.all()
                for child in children:
                    kids.append(child)
                    kids.extend(get_descendants(child))
                return kids
            descendants = get_descendants(related_person)
        
        return render(request, self.template_name, {
            'related_person': related_person,
            'ancestors': ancestors,
            'descendants': descendants
        })


class EditPersonView(LoginRequiredMixin, View):
    """编辑资料视图，允许用户编辑自己关联的人物信息"""
    template_name = 'genealogy/edit_person.html'
    
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
        
        related_person.name = request.POST.get('name', related_person.name)
        related_person.courtesy_name = request.POST.get('courtesy_name', related_person.courtesy_name)
        related_person.art_name = request.POST.get('art_name', related_person.art_name)
        related_person.alias = request.POST.get('alias', related_person.alias)
        related_person.generation_char = request.POST.get('generation_char', related_person.generation_char)
        related_person.birth_year = request.POST.get('birth_year') or None
        related_person.death_year = request.POST.get('death_year') or None
        related_person.birth_place = request.POST.get('birth_place', related_person.birth_place)
        related_person.burial_place = request.POST.get('burial_place', related_person.burial_place)
        related_person.burial_fengshui = request.POST.get('burial_fengshui', related_person.burial_fengshui)
        related_person.burial_direction = request.POST.get('burial_direction', related_person.burial_direction)
        related_person.biography = request.POST.get('biography', related_person.biography)
        related_person.achievements = request.POST.get('achievements', related_person.achievements)
        related_person.descendants_location = request.POST.get('descendants_location', related_person.descendants_location)
        
        if 'avatar' in request.FILES:
            related_person.avatar = request.FILES['avatar']
        
        related_person.save()
        
        return render(request, self.template_name, {
            'related_person': related_person,
            'success': '资料更新成功！'
        })
