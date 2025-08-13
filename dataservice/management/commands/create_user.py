from django.core.management.base import BaseCommand
from dataservice.models import User
import hashlib
from mongoengine.errors import NotUniqueError

def hash_password(password):
    """密码哈希"""
    return hashlib.sha256(password.encode()).hexdigest()

class Command(BaseCommand):
    help = '创建默认用户'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, help='用户名', default='admin')
        parser.add_argument('--password', type=str, help='密码', default='123456')
        parser.add_argument('--realname', type=str, help='真实姓名', default='系统管理员')
        parser.add_argument('--role', type=str, help='角色', default='admin')

    def handle(self, *args, **options):
        username = options['username']
        password = options['password']
        realname = options['realname']
        role = options['role']
        
        try:
            # 检查用户是否已存在
            existing_user = User.objects.filter(username=username).first()
            if existing_user:
                self.stdout.write(
                    self.style.WARNING(f'用户 {username} 已存在，跳过创建')
                )
                return
            
            # 创建用户
            user = User(
                username=username,
                password=hash_password(password),
                real_name=realname,
                roles=role,
                is_active=True
            )
            user.save()
            
            self.stdout.write(
                self.style.SUCCESS(f'成功创建用户: {username}')
            )
            self.stdout.write(f'用户名: {username}')
            self.stdout.write(f'密码: {password}')
            self.stdout.write(f'角色: {role}')
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'创建用户失败: {str(e)}')
            ) 