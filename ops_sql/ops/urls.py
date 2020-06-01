"""ops URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
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
from django.contrib import admin   #导入admin模块
from django.urls import path, re_path, include  #Django2.x中url路由导入path,re_path,include 函数
from django.views.generic import RedirectView   #导入通用类视图RedirectView用于简单的 HTTP 重定向
from .views import *               #导入当前views下所有模块

urlpatterns = [
    path('admin/', admin.site.urls),                                            #admin管理页
    path('favicon.ico', RedirectView.as_view(url=r'static/images/favicon.ico')),  #访问favicon.ico重定向url
    path('', IndexPage.as_view()),                                              #空值转Index页
    re_path(r'^login/$', LoginView.as_view()),                                  #login页
    re_path(r'logout/$', LogoutView.as_view()),                                 #logout页
    path('sqlmng/', include('sqlmng.urls')),                                    #匹配sqlmng,转发到sqlmng.urls二级路由文件
    path('account/', include('account.urls'))                                   #匹配account,转发到account.urls二级路由文件
]
