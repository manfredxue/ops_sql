#coding=utf-8
from django.conf.urls import re_path  #Django2.x版本导入正则路径
from .views import *

urlpatterns = [
    #re_path(r'^inception_result/(?P<pk>\d+)?/?(?P<actiontype>\w+)?$', InceptionHandleView.as_view(), name='inception_result'),
    re_path(r'^inception_result/(?P<pk>\d+)?/?$', InceptionHandleView.as_view(), name='inception_result'),      #inception_result结果页
    re_path(r'^inception_check/', InceptionCheckView.as_view(), name='inception_check'),                        #inception_check检测页
    re_path(r'^autoselect/', APISelectView.as_view(), name='autoselect'),                                       #自动选择页
    re_path(r'^optimize_check/', OptimizeCheckView.as_view(), name='optimize_check'),                           #优化检测页
    re_path(r'^dbconfig/(?P<pk>\d+)?/?$', DBView.as_view(), name='dbconfig'),                                   #数据库配置
]
