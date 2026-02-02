"""
刘氏乾正公族谱 - 应用路由配置
"""
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'genealogy'

urlpatterns = [
    # 首页
    path('', views.HomeView.as_view(), name='home'),
    
    # 世系图
    path('tree/', views.GenealogyTreeView.as_view(), name='tree'),
    
    # 人物列表
    path('persons/', views.PersonListView.as_view(), name='person_list'),
    
    # 人物详情
    path('person/<int:pk>/', views.PersonDetailView.as_view(), name='person_detail'),
    
    # 支系列表
    path('branches/', views.BranchListView.as_view(), name='branch_list'),
    
    # 支系详情
    path('branch/<int:pk>/', views.BranchDetailView.as_view(), name='branch_detail'),
    
    # 世代列表
    path('generations/', views.GenerationListView.as_view(), name='generation_list'),
    
    # 搜索
    path('search/', views.SearchView.as_view(), name='search'),
    
    # 用户认证
    path('login/', auth_views.LoginView.as_view(
        template_name='genealogy/login.html',
        redirect_authenticated_user=True
    ), name='login'),
    
    path('logout/', views.logout_view, name='logout'),
    
    # 修改密码
    path('password_change/', auth_views.PasswordChangeView.as_view(
        template_name='genealogy/password_change.html',
        success_url='/password_change/done/'
    ), name='password_change'),
    
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(
        template_name='genealogy/password_change_done.html'
    ), name='password_change_done'),
    
    # 用户注册
    path('register/', views.RegisterView.as_view(), name='register'),
    
    # 用户资料
    path('profile/', views.ProfileView.as_view(), name='profile'),
    
    # 编辑人物信息
    path('person/<int:pk>/edit/', views.PersonEditView.as_view(), name='person_edit'),
    
    # 我的家族
    path('my_family/', views.MyFamilyView.as_view(), name='my_family'),
    
    # 编辑自己的资料
    path('edit_person/', views.EditPersonView.as_view(), name='edit_person'),
    
    # 上传资料
    path('upload_media/', views.UploadMediaView.as_view(), name='upload_media'),
    
    # 获取世代选项（用于AJAX请求）
    path('get_generations/', views.get_generations, name='get_generations'),
    
    # 族谱记录
    path('records/', views.GenealogyRecordListView.as_view(), name='record_list'),
    path('record/<int:pk>/', views.GenealogyRecordDetailView.as_view(), name='record_detail'),
]
