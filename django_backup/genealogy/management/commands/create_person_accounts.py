"""
为人物创建默认用户账号的管理命令
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from genealogy.models import Person
import re


class Command(BaseCommand):
    help = '为人物创建默认用户账号'
    
    def handle(self, *args, **kwargs):
        # 获取所有没有关联用户的人物
        persons = Person.objects.filter(related_user__isnull=True)
        
        created_count = 0
        skipped_count = 0
        
        for person in persons:
            # 生成用户名（使用人物全名，移除特殊字符，转为小写）
            full_name = person.get_full_name()
            username = re.sub(r'[^\w\s]', '', full_name)
            username = username.replace(' ', '_').lower()
            
            # 确保用户名唯一
            base_username = username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}_{counter}"
                counter += 1
            
            try:
                # 创建用户
                user = User.objects.create_user(
                    username=username,
                    password='liu123',
                    email=f"{username}@example.com"
                )
                
                # 更新人物关联
                person.related_user = user
                person.account_status = 'inactive'  # 默认未激活
                person.save()
                
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'为 {person.get_full_name()} 创建账号: {username}'))
                
            except Exception as e:
                skipped_count += 1
                self.stdout.write(self.style.ERROR(f'为 {person.get_full_name()} 创建账号失败: {str(e)}'))
        
        self.stdout.write(self.style.SUCCESS(f'\n创建完成: 成功 {created_count} 个, 失败 {skipped_count} 个'))