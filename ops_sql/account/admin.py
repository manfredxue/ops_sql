# -*- coding: utf-8 -*-
from __future__ import unicode_literals  #统一所有字符串转为unicode类型
from .models import User                 #添加用户表
from django.contrib import admin

# Register your models here.

class UserAdmin(admin.ModelAdmin):      #用户管理界面添加列表显示元素
    list_display = (
        'username',
        'email',
        'role',                        #这样在Django admin界面添加role选项
        'remark',
    )

admin.site.register(User, UserAdmin)    #admin站点添加注册用户功能
