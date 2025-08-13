"""dpb2 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.static import serve   
from django.views.generic import TemplateView
from django.urls import re_path
from django.conf import settings
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('dataservice.urls')),
    # 常见静态目录（可选保留）
    re_path(r'^assets/(?P<path>.*)$', serve, {'document_root': settings.BASE_DIR / 'dist' / 'assets'}),
    # 常见根静态文件（可选）
    re_path(r'^(?P<path>(favicon\.ico|.*\.png|.*\.svg))$', serve, {'document_root': settings.BASE_DIR / 'dist'}),
    # 通用静态资源（包含根目录与各子目录下的 js/css/map/json/字体/图片/wasm 等）
    re_path(
        r'^(?P<path>.*\.(js|mjs|css|map|json|txt|webmanifest|ico|png|svg|jpg|jpeg|gif|webp|woff|woff2|ttf|eot|wasm))$',
        serve,
        {'document_root': settings.BASE_DIR / 'dist'}
    ),
    # SPA 路由回退（排除 /api/ 前缀）
    re_path(r'^(?!api/).*$', TemplateView.as_view(template_name='index.html')),
]
