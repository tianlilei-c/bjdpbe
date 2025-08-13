from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from django.http import Http404
from datetime import datetime, timedelta
import json
import jwt
import hashlib
from mongoengine.errors import DoesNotExist, NotUniqueError

from .models import SensorData, User, ManualPlan, DailyManualData
from .serializers import SensorDataSerializer, ManualPlanSerializer, DailyManualDataSerializer
from django.conf import settings

# JWT相关常量
JWT_SECRET = getattr(settings, 'JWT_SECRET', 'your-secret-key-for-jwt')
JWT_ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24小时

def generate_access_token(user_data):
    """生成访问令牌"""
    payload = {
        'user_id': str(user_data['id']),
        'username': user_data['username'],
        'exp': datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def verify_access_token(token):
    """验证访问令牌"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def hash_password(password):
    """密码哈希"""
    return hashlib.sha256(password.encode()).hexdigest()

class AuthViewSet(viewsets.ViewSet):
    """
    认证相关的API视图集
    """
    
    @action(detail=False, methods=['post'])
    def login(self, request):
        """
        用户登录
        
        请求体:
        {
            "username": "用户名",
            "password": "密码"
        }
        """
        username = request.data.get('username')
        password = request.data.get('password')
        
        if not username or not password:
            return Response({
                "code": 1,
                "message": "用户名和密码不能为空",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # 查找用户
            user = User.objects.get(username=username)
            
            # 验证密码
            if user.password != hash_password(password):
                return Response({
                    "code": 1,
                    "message": "用户名或密码错误",
                    "data": None
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            # 检查用户是否激活
            if not user.is_active:
                return Response({
                    "code": 1,
                    "message": "用户已被禁用",
                    "data": None
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            # 更新最后登录时间
            user.last_login = datetime.now()
            user.save()
            
            # 生成访问令牌
            user_data = {
                'id': str(user.id),
                'username': user.username,
                'real_name': user.real_name or user.username,
                'roles': [user.roles] if user.roles else ['user']
            }
            
            access_token = generate_access_token(user_data)
            
            return Response({
                "code": 0,
                "message": "登录成功",
                "data": {
                    "accessToken": access_token,
                    "username": user.username,
                    "realName": user.real_name or user.username,
                    "roles": [user.roles] if user.roles else ['user']
                }
            }, status=status.HTTP_200_OK)
            
        except DoesNotExist:
            return Response({
                "code": 1,
                "message": "用户名或密码错误",
                "data": None
            }, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({
                "code": 1,
                "message": f"登录失败: {str(e)}",
                "data": None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'])
    def logout(self, request):
        """
        用户登出
        """
        return Response({
            "code": 0,
            "message": "登出成功",
            "data": None
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'])
    def user_info(self, request):
        """
        获取当前用户信息
        需要在请求头中包含Authorization: Bearer <token>
        """
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return Response({
                "code": 1,
                "message": "未提供有效的访问令牌",
                "data": None
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        token = auth_header[7:]  # 移除 "Bearer " 前缀
        payload = verify_access_token(token)
        
        if not payload:
            return Response({
                "code": 1,
                "message": "访问令牌无效或已过期",
                "data": None
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            user = User.objects.get(id=payload['user_id'])
            return Response({
                "code": 0,
                "message": "获取用户信息成功",
                "data": {
                    "username": user.username,
                    "realName": user.real_name or user.username,
                    "roles": [user.roles] if user.roles else ['user'],
                    "email": user.email or ""
                }
            }, status=status.HTTP_200_OK)
            
        except DoesNotExist:
            return Response({
                "code": 1,
                "message": "用户不存在",
                "data": None
            }, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({
                "code": 1,
                "message": f"获取用户信息失败: {str(e)}",
                "data": None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def codes(self, request):
        """
        获取用户权限码（暂时返回空数组，后续可根据需要扩展）
        """
        return Response({
            "code": 0,
            "message": "获取权限码成功",
            "data": [
                'AC_100100',  # 用户管理权限
                'AC_100110',  # 创建用户权限
                'AC_100120',  # 编辑用户权限  
                'AC_100130',  # 删除用户权限
                'AC_200100',  # 数据管理权限
                'AC_200110',  # 查看传感器数据权限
                'AC_200120',  # 编辑传感器数据权限
                'AC_200130',  # 删除传感器数据权限
            ]
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get', 'post'])
    def users(self, request):
        """用户管理接口"""
        if request.method == 'GET':
            try:
                # 获取查询参数
                page = int(request.GET.get('page', 1))
                page_size = int(request.GET.get('page_size', 20))
                username = request.GET.get('username', '')
                roles = request.GET.get('roles', '')
                is_active = request.GET.get('is_active', '')
                
                # 构建查询条件
                query = {}
                if username:
                    query['username__icontains'] = username
                if roles:
                    query['roles'] = roles
                if is_active:
                    query['is_active'] = is_active.lower() == 'true'
                
                # 分页查询
                users = User.objects(**query).order_by('-created_at')
                total = users.count()
                
                start = (page - 1) * page_size
                end = start + page_size
                users_page = users[start:end]
                
                # 构建响应数据
                results = []
                for user in users_page:
                    results.append({
                        'id': str(user.id),
                        'username': user.username,
                        'real_name': user.real_name,
                        'email': user.email,
                        'roles': user.roles,
                        'is_active': user.is_active,
                        'created_at': user.created_at.isoformat() if user.created_at else None,
                        'last_login': user.last_login.isoformat() if user.last_login else None,
                    })
                
                return Response({
                    "code": 0,
                    "message": "获取用户列表成功",
                    "data": {
                        'count': total,
                        'next': None,
                        'previous': None,
                        'results': results
                    }
                }, status=status.HTTP_200_OK)
                
            except Exception as e:
                return Response({
                    "code": 1,
                    "message": f"获取用户列表失败: {str(e)}",
                    "data": None
                }, status=status.HTTP_200_OK)
        
        elif request.method == 'POST':
            try:
                username = request.data.get('username')
                password = request.data.get('password')
                real_name = request.data.get('real_name', '')
                email = request.data.get('email', '')
                roles = request.data.get('roles', 'admin')  # 默认设为admin
                
                if not username or not password:
                    return Response({
                        "code": 1,
                        "message": "用户名和密码不能为空",
                        "data": None
                    }, status=status.HTTP_200_OK)
                
                # 检查用户名是否已存在
                if User.objects(username=username).count() > 0:
                    return Response({
                        "code": 1,
                        "message": "用户名已存在",
                        "data": None
                    }, status=status.HTTP_200_OK)
                
                # 创建用户
                user = User(
                    username=username,
                    password=hash_password(password),
                    real_name=real_name,
                    email=email,
                    roles=roles,
                    created_at=datetime.now()
                )
                user.save()
                
                return Response({
                    "code": 0,
                    "message": "创建用户成功",
                    "data": {
                        'id': str(user.id),
                        'username': user.username,
                        'real_name': user.real_name,
                        'email': user.email,
                        'roles': user.roles,
                        'is_active': user.is_active,
                        'created_at': user.created_at.isoformat() if user.created_at else None,
                    }
                }, status=status.HTTP_200_OK)
                
            except Exception as e:
                return Response({
                    "code": 1,
                    "message": f"创建用户失败: {str(e)}",
                    "data": None
                }, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get', 'put', 'delete'])
    def user_detail(self, request, pk=None):
        """单个用户的详情、更新、删除接口"""
        try:
            user = User.objects.get(id=pk)
        except DoesNotExist:
            return Response({
                "code": 1,
                "message": "用户不存在",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)
        
        if request.method == 'GET':
            # 获取用户详情
            return Response({
                "code": 0,
                "message": "获取用户信息成功",
                "data": {
                    'id': str(user.id),
                    'username': user.username,
                    'real_name': user.real_name,
                    'email': user.email,
                    'roles': user.roles,
                    'is_active': user.is_active,
                    'created_at': user.created_at.isoformat() if user.created_at else None,
                    'last_login': user.last_login.isoformat() if user.last_login else None,
                }
            }, status=status.HTTP_200_OK)
        
        elif request.method == 'PUT':
            # 更新用户信息
            try:
                real_name = request.data.get('real_name', user.real_name)
                email = request.data.get('email', user.email)
                roles = request.data.get('roles', user.roles)
                is_active = request.data.get('is_active', user.is_active)
                
                # 更新用户信息
                user.real_name = real_name
                user.email = email
                user.roles = roles
                user.is_active = is_active
                user.save()
                
                return Response({
                    "code": 0,
                    "message": "更新用户信息成功",
                    "data": {
                        'id': str(user.id),
                        'username': user.username,
                        'real_name': user.real_name,
                        'email': user.email,
                        'roles': user.roles,
                        'is_active': user.is_active,
                        'created_at': user.created_at.isoformat() if user.created_at else None,
                        'last_login': user.last_login.isoformat() if user.last_login else None,
                    }
                }, status=status.HTTP_200_OK)
                
            except Exception as e:
                return Response({
                    "code": 1,
                    "message": f"更新用户信息失败: {str(e)}",
                    "data": None
                }, status=status.HTTP_200_OK)
        
        elif request.method == 'DELETE':
            # 删除用户
            try:
                # 不能删除管理员账户
                if user.username == 'admin':
                    return Response({
                        "code": 1,
                        "message": "不能删除管理员账户",
                        "data": None
                    }, status=status.HTTP_200_OK)
                
                user.delete()
                return Response({
                    "code": 0,
                    "message": "删除用户成功",
                    "data": None
                }, status=status.HTTP_200_OK)
                
            except Exception as e:
                return Response({
                    "code": 1,
                    "message": f"删除用户失败: {str(e)}",
                    "data": None
                }, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def reset_password(self, request, pk=None):
        """重置用户密码"""
        try:
            user = User.objects.get(id=pk)
        except DoesNotExist:
            return Response({
                "code": 1,
                "message": "用户不存在",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)
        
        try:
            new_password = request.data.get('new_password')
            if not new_password:
                return Response({
                    "code": 1,
                    "message": "新密码不能为空",
                    "data": None
                }, status=status.HTTP_200_OK)
            
            # 更新密码
            user.password = hash_password(new_password)
            user.save()
            
            return Response({
                "code": 0,
                "message": "密码重置成功",
                "data": None
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                "code": 1,
                "message": f"密码重置失败: {str(e)}",
                "data": None
            }, status=status.HTTP_200_OK)

class SensorDataPagination(PageNumberPagination):
    """
    自定义分页器
    """
    page_size = 100  # 默认每页数据量
    page_size_query_param = 'page_size'  # 允许客户端通过参数控制每页数据量
    max_page_size = 1000  # 每页最大数据量

class SensorDataViewSet(viewsets.ViewSet):
    """
    传感器数据的API视图集
    """
    pagination_class = SensorDataPagination
    
    def list(self, request):
        """
        列出所有传感器数据，支持时间范围筛选
        
        查询参数:
        - page: 页码 (默认1)
        - page_size: 每页数据量 (默认100)
        - start_time: 开始时间 (YYYY-MM-DD HH:MM:SS)
        - end_time: 结束时间 (YYYY-MM-DD HH:MM:SS)
        - field: 筛选特定字段 (例如 LDC_1)
        - value: 字段值 (用于筛选)
        - value_gt: 大于指定值
        - value_lt: 小于指定值
        """
        # 构建查询条件
        query_params = {}
        
        # 时间范围筛选
        if 'start_time' in request.query_params:
            try:
                start_time = datetime.strptime(request.query_params['start_time'], '%Y-%m-%d %H:%M:%S')
                query_params['timestamp__gte'] = start_time
            except ValueError:
                return Response({
                    "code": 1,
                    "message": "无效的开始时间格式，请使用YYYY-MM-DD HH:MM:SS",
                    "data": None
                }, status=status.HTTP_200_OK)
                
        if 'end_time' in request.query_params:
            try:
                end_time = datetime.strptime(request.query_params['end_time'], '%Y-%m-%d %H:%M:%S')
                query_params['timestamp__lte'] = end_time
            except ValueError:
                return Response({
                    "code": 1,
                    "message": "无效的结束时间格式，请使用YYYY-MM-DD HH:MM:SS",
                    "data": None
                }, status=status.HTTP_200_OK)
        
        # 字段值筛选
        if 'field' in request.query_params and 'value' in request.query_params:
            field = request.query_params['field']
            value = request.query_params['value']
            # 尝试转换为浮点数进行筛选
            try:
                value = float(value)
            except ValueError:
                pass
            query_params[field] = value
        
        # 大于/小于值筛选
        if 'field' in request.query_params and 'value_gt' in request.query_params:
            field = request.query_params['field']
            try:
                value = float(request.query_params['value_gt'])
                query_params[f"{field}__gt"] = value
            except ValueError:
                return Response({
                    "code": 1,
                    "message": "value_gt参数必须是数字",
                    "data": None
                }, status=status.HTTP_200_OK)
                
        if 'field' in request.query_params and 'value_lt' in request.query_params:
            field = request.query_params['field']
            try:
                value = float(request.query_params['value_lt'])
                query_params[f"{field}__lt"] = value
            except ValueError:
                return Response({
                    "code": 1,
                    "message": "value_lt参数必须是数字",
                    "data": None
                }, status=status.HTTP_200_OK)
        
        # 执行查询
        queryset = SensorData.objects(**query_params).order_by('-timestamp')
        
        # 手动分页处理
        try:
            page = int(request.query_params.get('page', 1))
            page_size = int(request.query_params.get('page_size', 100))
            
            # 确保页码和页面大小的有效性
            if page < 1:
                page = 1
            if page_size < 1:
                page_size = 100
            if page_size > 1000:  # 最大限制
                page_size = 1000
                
            # 计算总数
            total_count = queryset.count()
            
            # 计算分页偏移量
            start_index = (page - 1) * page_size
            end_index = start_index + page_size
            
            # 获取当前页数据
            page_data = list(queryset[start_index:end_index])
            
            # 序列化数据
            serializer = SensorDataSerializer(page_data, many=True)
            
            # 计算分页信息
            total_pages = (total_count + page_size - 1) // page_size
            has_next = page < total_pages
            has_previous = page > 1
            
            # 构建next和previous链接
            next_url = None
            previous_url = None
            
            if has_next:
                next_url = f"?page={page + 1}&page_size={page_size}"
            if has_previous:
                previous_url = f"?page={page - 1}&page_size={page_size}"
            
            # 返回分页结果
            return Response({
                "code": 0,
                "message": "获取传感器数据列表成功",
                "data": {
                    'count': total_count,
                    'next': next_url,
                    'previous': previous_url,
                    'results': serializer.data
                }
            }, status=status.HTTP_200_OK)
            
        except ValueError as e:
            return Response({
                "code": 1,
                "message": f"分页参数错误: {str(e)}",
                "data": None
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "code": 1,
                "message": f"查询失败: {str(e)}",
                "data": None
            }, status=status.HTTP_200_OK)
    
    def create(self, request):
        """
        创建一条或多条传感器数据
        
        支持单条数据或批量创建多条数据
        """
        # 检查是否为批量创建
        if isinstance(request.data, list):
            # 批量创建
            serializer = SensorDataSerializer(data=request.data, many=True)
            if serializer.is_valid():
                # 创建多个对象
                sensor_data_objects = []
                for item in serializer.validated_data:
                    sensor_data_objects.append(SensorData(**item))
                
                # 批量保存
                SensorData.objects.insert(sensor_data_objects)
                return Response({
                    "code": 0,
                    "message": f"成功创建{len(sensor_data_objects)}条传感器数据",
                    "data": serializer.data
                }, status=status.HTTP_200_OK)
            return Response({
                "code": 1,
                "message": "数据验证失败",
                "data": serializer.errors
            }, status=status.HTTP_200_OK)
        else:
            # 单条创建
            serializer = SensorDataSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "code": 0,
                    "message": "创建传感器数据成功",
                    "data": serializer.data
                }, status=status.HTTP_200_OK)
            return Response({
                "code": 1,
                "message": "数据验证失败",
                "data": serializer.errors
            }, status=status.HTTP_200_OK)
    
    def retrieve(self, request, pk=None):
        """
        获取单条传感器数据
        """
        try:
            sensor_data = SensorData.objects.get(id=pk)
            serializer = SensorDataSerializer(sensor_data)
            return Response({
                "code": 0,
                "message": "获取传感器数据成功",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        except DoesNotExist:
            return Response({
                "code": 1,
                "message": "传感器数据不存在",
                "data": None
            }, status=status.HTTP_200_OK)
    
    def update(self, request, pk=None):
        """
        更新传感器数据
        """
        try:
            sensor_data = SensorData.objects.get(id=pk)
            serializer = SensorDataSerializer(sensor_data, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "code": 0,
                    "message": "更新传感器数据成功",
                    "data": serializer.data
                }, status=status.HTTP_200_OK)
            return Response({
                "code": 1,
                "message": "数据验证失败",
                "data": serializer.errors
            }, status=status.HTTP_200_OK)
        except DoesNotExist:
            return Response({
                "code": 1,
                "message": "传感器数据不存在",
                "data": None
            }, status=status.HTTP_200_OK)
    
    def destroy(self, request, pk=None):
        """
        删除传感器数据
        """
        try:
            sensor_data = SensorData.objects.get(id=pk)
            sensor_data.delete()
            return Response({
                "code": 0,
                "message": "删除传感器数据成功",
                "data": None
            }, status=status.HTTP_200_OK)
        except DoesNotExist:
            return Response({
                "code": 1,
                "message": "传感器数据不存在",
                "data": None
            }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['delete'])
    def batch_delete(self, request):
        """
        批量删除传感器数据
        
        查询参数:
        - start_time: 开始时间 (YYYY-MM-DD HH:MM:SS)
        - end_time: 结束时间 (YYYY-MM-DD HH:MM:SS)
        """
        # 构建查询条件
        query_params = {}
        
        # 时间范围筛选
        if 'start_time' in request.query_params:
            try:
                start_time = datetime.strptime(request.query_params['start_time'], '%Y-%m-%d %H:%M:%S')
                query_params['timestamp__gte'] = start_time
            except ValueError:
                return Response({
                    "code": 1,
                    "message": "无效的开始时间格式，请使用YYYY-MM-DD HH:MM:SS",
                    "data": None
                }, status=status.HTTP_200_OK)
                
        if 'end_time' in request.query_params:
            try:
                end_time = datetime.strptime(request.query_params['end_time'], '%Y-%m-%d %H:%M:%S')
                query_params['timestamp__lte'] = end_time
            except ValueError:
                return Response({
                    "code": 1,
                    "message": "无效的结束时间格式，请使用YYYY-MM-DD HH:MM:SS",
                    "data": None
                }, status=status.HTTP_200_OK)
                
        # 执行批量删除
        try:
            result = SensorData.objects(**query_params).delete()
            return Response({
                "code": 0,
                "message": f"成功删除{result}条数据",
                "data": {"deleted_count": result}
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "code": 1,
                "message": f"批量删除失败: {str(e)}",
                "data": None
            }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'])
    def latest(self, request):
        """
        获取最新的传感器数据
        """
        try:
            latest_data = SensorData.objects.order_by('-timestamp').first()
            if latest_data:
                serializer = SensorDataSerializer(latest_data)
                return Response({
                    "code": 0,
                    "message": "获取最新数据成功",
                    "data": serializer.data
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    "code": 1,
                    "message": "没有数据",
                    "data": None
                }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "code": 1,
                "message": f"获取最新数据失败: {str(e)}",
                "data": None
            }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def download(self, request):
        """
        下载传感器数据为CSV文件
        
        查询参数:
        - start_time: 开始时间 (YYYY-MM-DD HH:MM:SS)
        - end_time: 结束时间 (YYYY-MM-DD HH:MM:SS)
        """
        try:
            import csv
            from django.http import HttpResponse
            
            # 构建查询条件
            query_params = {}
            
            # 时间范围筛选
            if 'start_time' in request.query_params:
                try:
                    start_time = datetime.strptime(request.query_params['start_time'], '%Y-%m-%d %H:%M:%S')
                    query_params['timestamp__gte'] = start_time
                except ValueError:
                    return Response({
                        "code": 1,
                        "message": "无效的开始时间格式，请使用YYYY-MM-DD HH:MM:SS",
                        "data": None
                    }, status=status.HTTP_200_OK)
                    
            if 'end_time' in request.query_params:
                try:
                    end_time = datetime.strptime(request.query_params['end_time'], '%Y-%m-%d %H:%M:%S')
                    query_params['timestamp__lte'] = end_time
                except ValueError:
                    return Response({
                        "code": 1,
                        "message": "无效的结束时间格式，请使用YYYY-MM-DD HH:MM:SS",
                        "data": None
                    }, status=status.HTTP_200_OK)
            
            # 执行查询
            queryset = SensorData.objects(**query_params).order_by('-timestamp')
            
            # 创建HTTP响应，设置为CSV文件下载
            response = HttpResponse(content_type='text/csv')
            filename = f'sensor_data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            
            # 添加BOM以支持Excel正确显示中文
            response.write('\ufeff')
            
            # 创建CSV写入器
            writer = csv.writer(response)
            
            # 写入标题行
            headers = [
                'ID', '时间戳', 
                '#1机负荷(MW)', '#2机负荷(MW)', '#3机负荷(MW)', '#4机负荷(MW)',
                '#1机五抽压力(MPa)', '#2机五抽压力(MPa)', '#3机五抽一路压力(MPa)', 
                '#3机五抽二路压力(MPa)', '#4机五抽一路压力(MPa)', '#4机五抽二路压力(MPa)',
                '汉沽实时热量(GJ/H)', '生态城实时热量(GJ/H)', '宁河实时热量(GJ/H)', '盐场实时流量(T/H)',
                '汉沽累计热量(GJ)', '生态城累计热量(GJ)', '宁河累计热量(GJ)', '盐场累计供汽量(GJ)',
                '海淡抽汽流量总和(T/H)'
            ]
            writer.writerow(headers)
            
            # 写入数据行
            for item in queryset:
                # 计算海淡抽汽流量总和
                haidian_total = (
                    (item.U1_FLOW or 0) + (item.U2_FLOW or 0) + (item.U3_FLOW or 0) + (item.U4_FLOW or 0) +
                    (item.U5_FLOW or 0) + (item.U6_FLOW or 0) + (item.U7_FLOW or 0) + (item.U8_FLOW or 0)
                )
                
                row = [
                    str(item.id),
                    item.timestamp.strftime('%Y-%m-%d %H:%M:%S') if item.timestamp else '',
                    item.LDC_1 or '', item.LDC_2 or '', item.LDC_3 or '', item.LDC_4 or '',
                    item.S5_01 or '', item.S5_02 or '', item.S5_0301 or '', 
                    item.S5_0302 or '', item.S5_0401 or '', item.S5_0402 or '',
                    item.HEATNOW_HG or '', item.HEATNOW_STC or '', item.HEATNOW_NH or '', item.STEAMNOW_YC or '',
                    item.HEATSUP_TOTAL_HG or '', item.HEATSUP_TOTAL_STC or '', 
                    item.HEATSUP_TOTAL_NH or '', item.STEAMSUP_TOTAL_YC or '',
                    round(haidian_total, 2) if haidian_total > 0 else ''
                ]
                writer.writerow(row)
            
            return response
            
        except Exception as e:
            return Response({
                "code": 1,
                "message": f"下载文件失败: {str(e)}",
                "data": None
                            }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def upload(self, request):
        """
        批量上传传感器数据（用于测试和数据导入）
        支持CSV文件上传或JSON数据上传
        """
        try:
            # 检查是否为文件上传
            if 'file' in request.FILES:
                # 处理CSV文件上传
                import csv
                import io
                
                uploaded_file = request.FILES['file']
                if not uploaded_file.name.endswith('.csv'):
                    return Response({
                        "code": 1,
                        "message": "只支持CSV文件格式",
                        "data": None
                    }, status=status.HTTP_200_OK)
                
                # 读取CSV文件内容
                try:
                    decoded_file = uploaded_file.read().decode('utf-8-sig')  # 支持BOM
                    csv_data = csv.DictReader(io.StringIO(decoded_file))
                    
                    created_count = 0
                    error_count = 0
                    
                    for row in csv_data:
                        try:
                            # 构建数据字典，处理空值
                            data = {}
                            for key, value in row.items():
                                if value and value.strip():
                                    # 将中文字段名映射到英文字段名
                                    field_mapping = {
                                        '时间戳': 'timestamp',
                                        '#1机负荷(MW)': 'LDC_1',
                                        '#2机负荷(MW)': 'LDC_2',
                                        '#3机负荷(MW)': 'LDC_3',
                                        '#4机负荷(MW)': 'LDC_4',
                                        '汉沽实时热量(GJ/H)': 'HEATNOW_HG',
                                        '生态城实时热量(GJ/H)': 'HEATNOW_STC',
                                        '宁河实时热量(GJ/H)': 'HEATNOW_NH',
                                        '盐场实时流量(T/H)': 'STEAMNOW_YC',
                                    }
                                    
                                    field_name = field_mapping.get(key, key)
                                    
                                    if field_name == 'timestamp':
                                        # 处理时间戳
                                        data[field_name] = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
                                    elif field_name in ['LDC_1', 'LDC_2', 'LDC_3', 'LDC_4', 
                                                        'HEATNOW_HG', 'HEATNOW_STC', 'HEATNOW_NH', 'STEAMNOW_YC']:
                                        # 处理数值字段
                                        data[field_name] = float(value)
                            
                            if data:  # 只有当有数据时才创建
                                serializer = SensorDataSerializer(data=data)
                                if serializer.is_valid():
                                    serializer.save()
                                    created_count += 1
                                else:
                                    error_count += 1
                                    print(f"数据验证失败: {serializer.errors}")
                        except Exception as e:
                            error_count += 1
                            print(f"处理行数据失败: {str(e)}")
                    
                    return Response({
                        "code": 0,
                        "message": f"文件上传完成，成功创建 {created_count} 条数据，失败 {error_count} 条",
                        "data": {"created": created_count, "errors": error_count}
                    }, status=status.HTTP_200_OK)
                    
                except Exception as e:
                    return Response({
                        "code": 1,
                        "message": f"文件解析失败: {str(e)}",
                        "data": None
                    }, status=status.HTTP_200_OK)
            
            # 处理JSON数据上传
            elif isinstance(request.data, dict) and 'generate_test_data' in request.data:
                # 生成测试数据
                import random
                from datetime import timedelta
                
                count = int(request.data.get('count', 100))
                start_time = datetime.now() - timedelta(days=7)
                
                test_data = []
                for i in range(count):
                    timestamp = start_time + timedelta(minutes=i * 5)  # 每5分钟一条数据
                    
                    data = {
                        'timestamp': timestamp,
                        'LDC_1': random.uniform(300, 600),
                        'LDC_2': random.uniform(300, 600),
                        'LDC_3': random.uniform(300, 600),
                        'LDC_4': random.uniform(300, 600),
                        'S5_01': random.uniform(2.0, 4.0),
                        'S5_02': random.uniform(2.0, 4.0),
                        'S5_0301': random.uniform(2.0, 4.0),
                        'S5_0302': random.uniform(2.0, 4.0),
                        'S5_0401': random.uniform(2.0, 4.0),
                        'S5_0402': random.uniform(2.0, 4.0),
                        'HEATNOW_HG': random.uniform(1000, 3000),
                        'HEATNOW_STC': random.uniform(800, 2000),
                        'HEATNOW_NH': random.uniform(1200, 2500),
                        'STEAMNOW_YC': random.uniform(800, 1500),
                        'HEATSUP_TOTAL_HG': random.uniform(50000, 100000),
                        'HEATSUP_TOTAL_STC': random.uniform(40000, 80000),
                        'HEATSUP_TOTAL_NH': random.uniform(60000, 120000),
                        'STEAMSUP_TOTAL_YC': random.uniform(30000, 60000),
                        'U1_FLOW': random.uniform(200, 500),
                        'U2_FLOW': random.uniform(200, 500),
                        'U3_FLOW': random.uniform(200, 500),
                        'U4_FLOW': random.uniform(200, 500),
                        'U5_FLOW': random.uniform(200, 500),
                        'U6_FLOW': random.uniform(200, 500),
                        'U7_FLOW': random.uniform(200, 500),
                        'U8_FLOW': random.uniform(200, 500),
                    }
                    test_data.append(SensorData(**data))
                
                # 批量创建
                SensorData.objects.insert(test_data)
                
                return Response({
                    "code": 0,
                    "message": f"成功生成 {count} 条测试数据",
                    "data": {"created": count}
                }, status=status.HTTP_200_OK)
            
            else:
                return Response({
                    "code": 1,
                    "message": "请上传CSV文件或提供有效的JSON数据",
                    "data": None
                }, status=status.HTTP_200_OK)
                
        except Exception as e:
            return Response({
                "code": 1,
                "message": f"上传失败: {str(e)}",
                "data": None
            }, status=status.HTTP_200_OK)

    def get_paginated_response(self, queryset, request):
        """
        返回分页结果 - 已弃用，现在在list方法中直接处理分页
        """
        # 这个方法已经不再使用，保留是为了向后兼容
        return self.list(request)


class ManualPlanViewSet(viewsets.ViewSet):
    """月计划 CRUD"""
    def list(self, request):
        items = ManualPlan.objects.order_by('-year', '-month')
        data = [ManualPlanSerializer(it).data for it in items]
        return Response({"code": 0, "message": "ok", "data": data}, status=status.HTTP_200_OK)

    def create(self, request):
        ser = ManualPlanSerializer(data=request.data)
        if ser.is_valid():
            obj = ManualPlan(**ser.validated_data)
            obj.save()
            return Response({"code": 0, "message": "created", "data": ManualPlanSerializer(obj).data}, status=status.HTTP_200_OK)
        return Response({"code": 1, "message": "invalid", "data": ser.errors}, status=status.HTTP_200_OK)

    def update(self, request, pk=None):
        try:
            obj = ManualPlan.objects.get(id=pk)
        except DoesNotExist:
            return Response({"code": 1, "message": "not found", "data": None}, status=status.HTTP_404_NOT_FOUND)
        ser = ManualPlanSerializer(obj, data=request.data, partial=True)
        if ser.is_valid():
            for k, v in ser.validated_data.items():
                setattr(obj, k, v)
            obj.save()
            return Response({"code": 0, "message": "updated", "data": ManualPlanSerializer(obj).data}, status=status.HTTP_200_OK)
        return Response({"code": 1, "message": "invalid", "data": ser.errors}, status=status.HTTP_200_OK)

    def destroy(self, request, pk=None):
        try:
            obj = ManualPlan.objects.get(id=pk)
            obj.delete()
            return Response({"code": 0, "message": "deleted", "data": None}, status=status.HTTP_200_OK)
        except DoesNotExist:
            return Response({"code": 1, "message": "not found", "data": None}, status=status.HTTP_404_NOT_FOUND)


class DailyManualDataViewSet(viewsets.ViewSet):
    """日度手动数据 CRUD"""
    def list(self, request):
        items = DailyManualData.objects.order_by('-date')
        data = [DailyManualDataSerializer(it).data for it in items]
        return Response({"code": 0, "message": "ok", "data": data}, status=status.HTTP_200_OK)

    def create(self, request):
        ser = DailyManualDataSerializer(data=request.data)
        if ser.is_valid():
            obj = DailyManualData(**ser.validated_data)
            obj.save()
            return Response({"code": 0, "message": "created", "data": DailyManualDataSerializer(obj).data}, status=status.HTTP_200_OK)
        return Response({"code": 1, "message": "invalid", "data": ser.errors}, status=status.HTTP_200_OK)

    def update(self, request, pk=None):
        try:
            obj = DailyManualData.objects.get(id=pk)
        except DoesNotExist:
            return Response({"code": 1, "message": "not found", "data": None}, status=status.HTTP_404_NOT_FOUND)
        ser = DailyManualDataSerializer(obj, data=request.data, partial=True)
        if ser.is_valid():
            for k, v in ser.validated_data.items():
                setattr(obj, k, v)
            obj.save()
            return Response({"code": 0, "message": "updated", "data": DailyManualDataSerializer(obj).data}, status=status.HTTP_200_OK)
        return Response({"code": 1, "message": "invalid", "data": ser.errors}, status=status.HTTP_200_OK)

    def destroy(self, request, pk=None):
        try:
            obj = DailyManualData.objects.get(id=pk)
            obj.delete()
            return Response({"code": 0, "message": "deleted", "data": None}, status=status.HTTP_200_OK)
        except DoesNotExist:
            return Response({"code": 1, "message": "not found", "data": None}, status=status.HTTP_404_NOT_FOUND)
