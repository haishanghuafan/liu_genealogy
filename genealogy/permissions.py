"""
自定义权限类
"""
from django.contrib.auth.mixins import AccessMixin
from django.shortcuts import get_object_or_404
from django.http import HttpResponseForbidden
from genealogy.models import Person


class PersonOwnerMixin(AccessMixin):
    """确保用户只能访问自己关联的人物信息"""
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        
        # 获取人物对象
        person_id = kwargs.get('pk')
        person = get_object_or_404(Person, pk=person_id)
        
        # 检查权限
        # 1. 管理员可以访问所有
        if request.user.is_staff:
            return super().dispatch(request, *args, **kwargs)
        
        # 2. 用户只能访问自己关联的人物
        if person.related_user == request.user:
            return super().dispatch(request, *args, **kwargs)
        
        # 3. 其他情况禁止访问
        return HttpResponseForbidden("您没有权限访问此人物信息")