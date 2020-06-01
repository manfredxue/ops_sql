#coding=utf-8
import re, subprocess                                       #导入re正则，subprocess子进程模块
from django.conf import settings                            #引用django配置文件中设置对象
from django.views.generic import View, TemplateView         #View基于类视图，改造通用类视图成TemplateView get带传参data
from utils.baseviews import BaseListView                    #基于类视图BaseListView
from django.contrib.auth.mixins import LoginRequiredMixin   #验证登录用户类型和权限
from django.http import QueryDict,JsonResponse              #后端获取前段数据放在QueryDict集中,JsonResponse返回Json格式
from utils.dbcrypt import prpcrypt                          #导入prpcrypt加密模块
from utils.wrappers import handle_save_data, handle_check_permission #调用自写wrappers装饰器,保存数据，检查自定义权限
from utils.inception_tool import table_structure, get_bak   #导入table_structure, get_bak自定义模块

from .models import *

# Create your views here.


# 数据库配置
class DBView(BaseListView):

    model = DBConf
    template_name = 'sqlmng/dbconfig.html'
    # HTTP中get请求，put修改，post创建，delete删除
    def get_queryset(self):                                       #查询函数
        search = self.request.GET.get('search', '')               #查询集
        return self.model.objects.filter(name__contains=search)   #过滤条件
    # HTTP中get请求，put修改，post创建，delete删除
    @handle_save_data
    def post(self, request, **kwargs):                            #创建数据
        data = QueryDict(request.body).dict()                     #取前端整条记录
        password = data.get('password')                           #取前端密码字段值
        # 对password加密
        cry_password = prpcrypt.encrypt(password)                 #对明文加密
        # 替换data的password
        data['password'] = cry_password
        # 写入数据库
        self.model.objects.create(**data)                        #创建记录
        return JsonResponse({'status': 0})                       #返回正常状态值0

    def delete(self, request, **kwargs):                         #删除数据
        self.model.objects.get(pk=kwargs.get('pk')).delete()     #删除记录
        return JsonResponse({'status': 0})

    @handle_save_data
    def put(self, request, **kwargs):                           #修改数据
        # 密码的修改逻辑：如果密码没变化就直接保存，有变化就加密后保存
        data = QueryDict(request.body).dict()                   #取前端整条记录
        pk = kwargs.get('pk')                                   #取id
        obj = self.model.objects.get(pk=pk)                     #取后端数据库对应记录
        password = data.get('password')                         #取前端密码字段值
        if obj.password != password:  # 密码被做了修改           #后前端密码不一致
            data['password'] = prpcrypt.encrypt(password)       #加密新密码后存入数据库
        self.model.objects.filter(pk=pk).update(**data)         #更新记录
        return JsonResponse({'status': 0})


class APISelectView(LoginRequiredMixin, View):                  #选择视图接口，检查登录用户是否有权限

    model_db = DBConf                                           #DBConf表
    # HTTP中get请求，put修改，post创建，delete删除
    def post(self, request):  # 前端切换环境时，返回相应的数据（执行人，数据库名） #创建数据
        data = QueryDict(request.body).dict()                   #取前端整条记录
        env = data.get('env')                                   #执行环境：生产或测试
        ret = dict()
        ret['dbs'] = [db.name for db in self.model_db.objects.filter(env=env)]  #生产库或测试库名
        user = request.user                                    #取前端用户记录
        username = user.username                               #取前端用户名
        if user.is_superuser:  # 超级用户，执行人是自己
            ret['treater_list'] = [username]                   #treater执行人放入列表
            return JsonResponse(ret)
        role = user.role
        if env == '2':  # 测试环境，执行人就是自己
            treater_list = [username]                         #测试环境自己执行
        elif env == '1':  # 生产环境                           #生产环境管理自己执行，研发无权执行
            if role in ['1', '2']:  # 经理/总监，执行人是自己
                treater_list = [username]
            elif role == '3':  # 研发，找出他组内的经理列表     #生产环境研发找上级执行
                ug = user.groups.first()                      #用户组表第一条记录
                if ug:  # 用户有组
                    group_users = ug.user_set.all()           #所有记录集
                    treater_list = [u.username for u in group_users if u.role == '2'] #找出总监角色的用户
                else:
                    treater_list = []                         #其他角色用户
        ret['treater_list'] = treater_list                    #赋值执行人列表
        return JsonResponse(ret)


class InceptionCheckView(LoginRequiredMixin, TemplateView):  #检查视图

    model = InceptionSql
    model_db = DBConf
    template_name = 'sqlmng/inception_check.html'
    # HTTP中get请求，put修改，post创建，delete删除
    def post(self, request):                              #创建数据
        data = QueryDict(request.body).dict()             #取前端整条记录
        user = request.user                               #取前端用户
        sql_content = data.get('sql_content')             #sql语句
        db_name = data.get('db_name')                     #db名
        treater = data.get('treater')                     #执行人
        env = data.get('env')                             #执行环境
        # 根据选择的数据库环境，匹配地址
        object_db = self.model_db.objects.get(name=db_name, env=env)   #选择出db
        password = prpcrypt.decrypt(object_db.password)   #解密db密码
        connection = '--user=%s; --password=%s; --host=%s; --port=%s; --enable-check;' % \
                     (object_db.user, password, object_db.host, object_db.port)
        result, status = table_structure(connection, db_name, sql_content)  # 审核
        if status == -1:                                         # 错误1：调函数异常
            return JsonResponse({'status': -2, 'msg': result})   # 错误2：审核的SQL语句有语法错误
        # 判断检测错误，有则返回
        error_info = []                                  #错误信息
        for i in result:
            if i[4] != 'None':                                 #i[4]=inception_status_tag
                error_info.append(i[4])                 #追加状态tag
        if error_info:
            return JsonResponse({'status': -2, 'msg': error_info})  #返回语法错误
        # 审核通过，写入数据库
        # 从数据库获取committer提交人和treater执行人的信息（没有的话写入）
        treater = User.objects.get_or_create(username=treater)  # 执行人数据
        committer = User.objects.get(username=user.username)  # 提交人数据（是一定有的，因为他提交的SQL 所以他必然登录过了）
        # 写入sql信息
        data['committer'] = user.username                #提交人
        object_sql = self.model.objects.create(**data)   #创建记录
        object_sql.sql_users.add(treater[0], committer)  #sql用户关联表添加执行人，提交人
        return JsonResponse({'status': 0})


class InceptionHandleView(BaseListView):                    #处理视图

    template_name = 'sqlmng/inception_result.html'
    template_detail = 'sqlmng/inception_sqldetail.html'
    model_db = DBConf
    model = InceptionSql  # 数据模型名
    #不同权限和用户查询数据库
    def get_queryset(self):  # 数据库查询的结果，对应于context_object_name
        user = self.request.user
        role = user.role
        if user.is_superuser:  # 管理员
            queryset = self.model.objects.all()           #取所有记录集
        elif role == '1':  # 总监
            queryset = self.model.objects.filter(commiter=user.username)
            g = user.groups.first()  # 组
            for u in g.user_set.values():  # 遍历组内所有的用户
                user_queryset = self.model.objects.filter(commiter=u['username'], env=1)
                queryset = queryset | user_queryset
        else:  # 研发或经理
            queryset = user.inceptionsql_set.all()
        return queryset

    # 执行/回滚/放弃...
    @handle_check_permission
    def post(self, request, *args, **kwargs):            #创建数据
        data = QueryDict(request.body).dict()            #取前端整条记录
        pk = data.get('inception_id')                    #取前端id
        action_type = data.get('action_type')            #动作类型：execute执行 rollback回滚 reject放弃
        object_sql = self.model.objects.get(pk=pk)       #取SQL语句
        db_name = object_sql.db_name                     # 取数据库名
        env = object_sql.env                             #执行环境
        # 根据选择的数据库环境，匹配地址
        object_db = self.model_db.objects.filter(name=db_name, env=env)[0]
        password = prpcrypt.decrypt(object_db.password)
        connection = '--user=%s; --password=%s; --host=%s; --port=%s; --enable-execute;' % \
                     (object_db.user, password, object_db.host, object_db.port)
        ret = {'status': 0}   #成功
        if action_type == 'execute':  #执行，扩充sql详细语句
            sql_content = object_sql.sql_content
            execute_info, status = table_structure(connection, db_name, sql_content)  # 遇到错误的语句，包括它后面的都不会执行 只检查
            # 改变本条sql的状态
            affected_rows = 0
            execute_time = 0
            opid_list = []
            for rz in execute_info:
                rz_tag = rz[4]
                if rz_tag == 'None' or re.findall('Warning', rz_tag):  # 执行成功
                    ret['Warning'] = ""
                    if re.findall('Warning', rz_tag):
                        ret['Warning'] = rz_tag
                    object_sql.status = 0
                    # 执行结果，受影响的条数，执行所耗时间，回滚语句
                    object_sql.rollback_db = rz[8]
                    affected_rows += rz[6]
                    execute_time += float(rz[9])
                    opid_list.append(rz[7].replace("'", ""))  # rz[7].replace("'","")  : 每条sql执行后的回滚opid
                else:  # 执行失败的结果
                    object_sql.status = 2
                    object_sql.execute_info = execute_info
                    ret['msg'] = rz_tag
                    ret['status'] = -1
                    break
            object_sql.rollback_id = opid_list
            object_sql.exe_affected_rows = affected_rows
            ret['affected_rows'] = affected_rows
            ret['execute_time'] = '%.3f' % execute_time  # 保留3位小数
        elif action_type == 'reject':
            object_sql.status = 1
        elif action_type == 'rollback':  # 回滚
            rollback_id = object_sql.rollback_id
            rollback_db = object_sql.rollback_db  # 回滚库
            # 拼接回滚语句
            rollback_sqls = ''  # 回滚语句
            for opid in eval(rollback_id)[1:]:
                # 1 从回滚总表中获取表名
                rollback_source = 'select tablename from $_$Inception_backup_information$_$ where opid_time = "%s" ' % opid
                rollback_table = get_bak(rollback_source, rollback_db)[0][0]
                # 2 从回滚子表中获取回滚语句
                rollback_content = 'select rollback_statement from %s.%s where opid_time = "%s" ' % (rollback_db, rollback_table, opid)
                per_rollback = get_bak(rollback_content)  # 获取回滚数据
                for i in per_rollback:  # 累加拼接
                    rollback_sqls += i[0]
            # 拼接回滚语句 执行回滚操作，修改sql状态
            execute_info, status = table_structure(connection, db_name, rollback_sqls)
            object_sql.status = -2
            roll_affected_rows = len(execute_info) - 1
            object_sql.roll_affected_rows = roll_affected_rows
            ret['roll_affected_rows'] = roll_affected_rows  # 执行回滚语句的结果，除去第一个use 数据库的
        object_sql.save()
        return JsonResponse(ret)


# 优化（针对select语句，要带查询条件）
class OptimizeCheckView(LoginRequiredMixin, TemplateView):

    model_db = DBConf
    template_name = 'sqlmng/optimize_check.html'

    def post(self, request, **kwargs):
        data = QueryDict(request.body).dict()
        sql_content = data.get('sql_content').replace('`', '')
        db_name = data.get('db_name')
        env = data.get('env', 1)
        object_db = self.model_db.objects.get(name=db_name, env=env)
        password = prpcrypt.decrypt(object_db.password)  # 解密
        optimize_bin = settings.OPTIMIZE_BIN
        cmd = ''' %s -h %s -u %s -p %s -P %s -v 1 -d %s  -q "%s" ''' % \
              (optimize_bin, object_db.host, object_db.user, password, object_db.port, db_name, sql_content)
        res = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        res = res.stdout.read().decode('utf-8')
        return JsonResponse({'status': 0, 'data': res})
