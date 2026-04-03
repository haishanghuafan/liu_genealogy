"""
URL configuration for liu_genealogy project.

刘氏乾正公族谱网站 - 主路由配置
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Admin site settings
admin.site.site_header = '刘氏乾正公族谱 - 管理后台'
admin.site.site_title = '刘氏乾正公族谱管理'
admin.site.index_title = '族谱管理'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('genealogy.urls', namespace='genealogy')),
]

# 为静态文件和媒体文件提供服务
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
