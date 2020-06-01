# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import AbstractUser  #引入AbstractUser类用于继承


class User(AbstractUser):    #自定义User类表替换系统User表
    ROLES = (
        ('1', u'总监'),
        ('2', u'经理'),
        ('3', u'研发'),
    )
    role = models.CharField(max_length=32, default='3', choices=ROLES)   #扩展字段：角色
    remark = models.CharField(max_length=128, default='', blank=True)    #扩展字段：备注

    class Meta:
        verbose_name_plural = u'用户'   #定义元数据, 按用户名倒序排序
        ordering = ['-id']

    def __unicode__(self):              #美化打印
        return self.username

    @property                            #装饰器
    def to_dict(self):                   #定义字典函数并序列化成列表
        ret = dict()                     #字典完整赋值变量ret，初始化
        for attr in [f.name for f in self._meta.fields]:  #如果f.name字段在所有元字段内，取f.name对象的attr属性
            value = getattr(self, attr)
            ret[attr] = value            #赋值不同列表ret, 下标attr,值value
        group = self.groups.first()      #获取groups对象的第一个元素
        ret['group'] = group.name if group else ''   #赋值列表，下标'group',值group中name
        return ret
