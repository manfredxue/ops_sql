
# -*- coding: utf-8 -*-
from functools import wraps
from django.http import QueryDict, JsonResponse
from sqlmng.models import InceptionSql
#字典：权限地图，就是二维表
perm_map = {
    'execute': {               #执行
        'status': [-1],
        'env':{
            1: ['admin', '1', '2'],
            2: ['admin', '1', '2', '3']
        }
    },
    'rollback': {            #回滚
        'status': [0],
        'env': {
            1: ['admin', '1', '2'],
            2: ['admin', '1', '2', '3']
        }
    },
    'reject': {             #拒绝
        'status': [-1],
        'env': {
            1: ['admin', '1', '2'],
            2: ['admin', '1', '2', '3']
        }
    }
}

#装饰器保存数据状态
def handle_save_data(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            code = e.args[0]
            if code == 1062:
                status = -1
                msg = e.args[1]
            else:
                status = -2
                msg = e.args[0]
            return JsonResponse({'status': status, 'msg': msg})
    return wrapper

#装饰器检查权限
def handle_check_permission(func):
    @wraps(func)
    def wrapper(obj, *args, **kwargs):
        user = obj.request.user
        data = QueryDict(obj.request.body).dict()
        pk = data.get('inception_id')                     #id
        object_sql = InceptionSql.objects.get(pk=pk)      #查询到SQL语句
        env = object_sql.env                              #环境
        status = object_sql.status                         #状态
        action_type = data.get('action_type')              #动作类型
        role = 'admin' if user.is_superuser else user.role
        perm = perm_map[action_type]                       #状态列表
        if status in perm['status'] and role in perm['env'][env]:
            return func(obj, *args, **kwargs)
        else:
            return JsonResponse({'status': 403, 'msg': '当前无权限 {}'.format(action_type)})
    return wrapper
