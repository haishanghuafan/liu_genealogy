"""
访问量统计中间件
"""
from .models import PageView, DailyVisitStats, PageVisitStats
from django.utils import timezone
from datetime import datetime, timedelta


class VisitTrackingMiddleware:
    """访问跟踪中间件"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        # 不需要跟踪的URL路径
        self.excluded_paths = [
            '/static/',
            '/media/',
            '/admin/',
            '/favicon.ico',
            '/robots.txt',
            '/sitemap.xml',
        ]
    
    def __call__(self, request):
        # 在视图处理之前记录访问
        response = self.get_response(request)
        
        # 只记录成功的GET请求
        if request.method == 'GET' and response.status_code == 200:
            self.track_visit(request)
        
        return response
    
    def should_track(self, path):
        """检查是否应该跟踪该路径"""
        for excluded in self.excluded_paths:
            if path.startswith(excluded):
                return False
        return True
    
    def get_client_ip(self, request):
        """获取客户端真实IP地址"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def track_visit(self, request):
        """记录访问"""
        path = request.path
        
        # 检查是否需要跟踪
        if not self.should_track(path):
            return
        
        # 获取客户端信息
        ip_address = self.get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')[:500]
        referer = request.META.get('HTTP_REFERER', '')[:500]
        session_key = request.session.session_key or ''
        user = request.user if request.user.is_authenticated else None
        
        # 检查是否是独立访问（24小时内同一IP同一页面只算一次）
        today = timezone.now().date()
        is_unique = not PageView.objects.filter(
            path=path,
            ip_address=ip_address,
            visit_date=today
        ).exists()
        
        # 创建访问记录
        try:
            PageView.objects.create(
                url=request.build_absolute_uri(),
                path=path,
                ip_address=ip_address,
                user_agent=user_agent,
                referer=referer,
                session_key=session_key,
                user=user,
                is_unique_visit=is_unique,
                visit_date=today
            )
            
            # 更新每日统计
            self.update_daily_stats(today)
            
            # 更新页面统计
            self.update_page_stats(path)
            
        except Exception:
            # 记录访问失败不应影响正常请求
            pass
    
    def update_daily_stats(self, date):
        """更新每日访问统计"""
        try:
            stats, created = DailyVisitStats.objects.get_or_create(
                date=date,
                defaults={
                    'total_visits': 0,
                    'unique_visitors': 0,
                    'unique_ips': 0
                }
            )
            
            # 重新计算统计数据
            daily_visits = PageView.objects.filter(visit_date=date)
            stats.total_visits = daily_visits.count()
            stats.unique_visitors = daily_visits.filter(is_unique_visit=True).count()
            stats.unique_ips = daily_visits.values('ip_address').distinct().count()
            stats.save()
            
        except Exception:
            pass
    
    def update_page_stats(self, path):
        """更新页面访问统计"""
        try:
            stats, created = PageVisitStats.objects.get_or_create(
                path=path,
                defaults={
                    'total_visits': 0,
                    'unique_visitors': 0
                }
            )
            
            # 重新计算统计数据
            page_visits = PageView.objects.filter(path=path)
            stats.total_visits = page_visits.count()
            stats.unique_visitors = page_visits.filter(is_unique_visit=True).count()
            stats.save()
            
        except Exception:
            pass
