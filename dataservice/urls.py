from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SensorDataViewSet, AuthViewSet, ManualPlanViewSet, DailyManualDataViewSet, WeatherViewSet, PredictViewSet

# 创建路由器并注册视图集
router = DefaultRouter()
router.register(r'sensor-data', SensorDataViewSet, basename='sensor-data')
router.register(r'auth', AuthViewSet, basename='auth')
router.register(r'manual-plan', ManualPlanViewSet, basename='manual-plan')
router.register(r'manual-day', DailyManualDataViewSet, basename='manual-day')
router.register(r'weather', WeatherViewSet, basename='weather')
router.register(r'predict', PredictViewSet, basename='predict')

urlpatterns = [
    path('', include(router.urls)),
    # 添加用户详情路由
    path('auth/users/<str:pk>/', AuthViewSet.as_view({'get': 'user_detail', 'put': 'user_detail', 'delete': 'user_detail'}), name='user-detail'),
    path('auth/users/<str:pk>/reset_password/', AuthViewSet.as_view({'post': 'reset_password'}), name='user-reset-password'),
] 