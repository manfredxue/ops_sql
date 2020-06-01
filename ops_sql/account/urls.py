from django.urls import path, re_path   #Django2.x导入path, re_path正则路径
from .views import *

urlpatterns = [
    re_path(r'^users/(?P<pk>\d+)?/?$', UserView.as_view()),        #匹配users/开头后跟id等内容，传递给视图函数，用户页
    re_path(r'^groups/(?P<pk>\d+)?/?$', GroupView.as_view()),      #用户组页
    re_path(r'^api_groups/(?P<pk>\d+)?/?$', APIGroupView.as_view()),  #用户组接口页
]
