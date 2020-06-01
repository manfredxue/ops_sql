#coding=utf-8
from __future__ import unicode_literals  #引入AbstractUser类用于继承

from django.db import models             #导入数据库
from account.models import User          #导入用户表

# Create your models here.


class BaseModel(models.Model):          #定义基础类表，由别表来继承。新表不用设这些字段
    '''
       基础表(抽象类)
    '''
    name = models.CharField(max_length=32, verbose_name='名字')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='修改时间')
    remark = models.TextField(default='', null=True, blank=True, verbose_name='备注')

    @property                          #装饰器在BaseModel类中
    def to_dict_base(self):            #定义字典基类并序列化成基础列表
        ret = dict()                   #字典完整赋值变量ret
        for attr in [f.name for f in self._meta.fields]:  #如果f.name字段在所有元字段内，取f.name对象的attr属性
            value = getattr(self, attr)  #获取self对象的属性值
            ret[attr] = value          #赋值不同列表ret, 下标attr,值value
        return ret

    def __unicode__(self):             #美化打印
        return self.name  # 显示对象的名字

    class Meta:                        #嵌套类，给上级类定义功能
        abstract = True  # 抽象类
        ordering = ['-id']  # 按id倒排


class InceptionSql(BaseModel):      #定义InceptionSql继承自基础类表
    SQL_STATUS = (
        (-2, u'已回滚'),
        (-1, u'待执行'),
        (0, u'执行成功'),
        (1, u'已放弃'),
        (2, u'执行失败'),
    )

    ENV = (
        (1, u'生产环境'),
        (2, u'测试环境')
    )

    sql_users = models.ManyToManyField(User)
    committer = models.CharField(max_length=20)
    sql_content = models.TextField(blank=True, null=True)
    env = models.IntegerField(choices=ENV)
    db_name = models.CharField(max_length=50)
    treater = models.CharField(max_length=20)
    status = models.IntegerField(default=-1, choices=SQL_STATUS)
    execute_info = models.TextField(default='', null=True, blank=True)
    exe_affected_rows = models.CharField(max_length=10)
    roll_affected_rows = models.CharField(max_length=10)
    rollback_id = models.TextField(blank=True, null=True)
    rollback_db = models.CharField(max_length=100)

    @property
    def to_dict(self):
        ret = self.to_dict_base
        return ret

class DBConf(BaseModel):
    GENDER_CHOICES = (
        (1, u'生产'),
        (2, u'测试'),
    )
    user = models.CharField(max_length=128)
    password = models.CharField(max_length=128)
    host = models.CharField(max_length=16)
    port = models.CharField(max_length=5)
    env = models.IntegerField(blank=True, null=True, choices=GENDER_CHOICES)

    class Meta:
        unique_together = ('name', 'host', 'env', 'port')
        ordering = ['-id']  # 按id倒排