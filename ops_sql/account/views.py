
from django.contrib.auth.models import Group  #导入auth_permission模块表group
from django.http import QueryDict, JsonResponse    #后端获取前段数据放在QueryDict集中,JsonResponse返回Json格式
from utils.baseviews import BaseListView, BaseAPIView  #基于类视图BaseAPIView, BaseListView
from utils.wrappers import handle_save_data #调用自写wrappers装饰器,保证各个字段输入合法性,不会太长乱码异常格式等
from .models import User  #导入内置User表


class UserView(BaseListView):              #定义UserView视图继承自基类视图BaseListView
    """用户页增改删"""
    model = User                           #模块表User
    template_name = 'account/users.html'   #模板即前端页

    def get_queryset(self):                           #查询功能
        queryset = self.model.objects.all()           #导入对象所有查询记录
        search = self.request.GET.get('search')       #search功能单独写函数, 前端页面传参内容做search,获取不到则为空
        if search:
            queryset = queryset.filter(username__contains=search) #过滤条件用户名包含查询条件
        queryset = [user.to_dict for user in queryset] #用户如在查询集中，用户进字典进查询集
        return queryset                    #返回查询集列表

    # HTTP中get请求，put修改，post创建，delete删除
    @handle_save_data #调用处理数据保存装饰器
    def post(self, request, *args, **kwargs):       #向前端创建数据密码并保存后端数据库,创建数据
        data = QueryDict(request.body).dict()       #从前端获取http.request的数据放到字典QueryDict
        password = data.get('password')             #获密码值
        group_name = data.pop('group_name')         #删除组名并赋值
        user = self.model.objects.create(**data)    #使用字典直接创建并保存数据库记录
        user.set_password(password)                 #用户记录加密明文HASH密码
        user.save()                                 #用户表保存
        group_qs = Group.objects.filter(name=group_name)   #按组名查询
        if group_qs:                                #如存在
            user.groups.add(group_qs[0])            #用户组关联表添加group_qs对象第一个元素id
        return JsonResponse({'status': 1})          #返回状态码1 正常

    @handle_save_data
    def put(self, request, *args, **kwargs):       #向前端修改数据密码，修改数据
        pk = kwargs.get('pk')                      #取id值，view函数有关键字id不能用
        data = QueryDict(request.body).dict()      #从前端获取http.request的数据放到字典QueryDict
        password = data.pop('password')            #删除记录里密码并赋值
        group_name = data.pop('group_name')        #删除记录里组名并赋值
        user_qs = self.model.objects.filter(pk=pk) #后端数据库查询到此记录
        user_qs.update(**data)                     #用前端查到记录更新到数据库
        user = user_qs[0]                          #用户记录的第一个元素，用户id
        old_password = user.password               #数据表中用户当前密码存入老密码
        if password != old_password:               #前端密码不同于后端老密码
            user.set_password(password)            #用户记录加密明文HASH密码
            user.save()                            #用户表保存
        group_qs = Group.objects.filter(name=group_name)   #按组名查询
        if group_qs:                               #如存在
            user.groups.set([group_qs[0]])         #用户组关联表设置group_qs对象第一个元素id
        return JsonResponse({'status': 1})         #返回状态码1 正常


class GroupView(BaseListView):    #定义GroupView视图继承自基类视图BaseListView

    model = Group                                  #模块表Group
    template_name = 'account/groups.html'          #模板即前端页

    def get_queryset(self):                              #查询功能
        queryset = self.model.objects.order_by('-id')    #导入对象所有查询记录按id倒序排列
        search = self.request.GET.get('search')          #前端页面传参内容做search,获取不到则为空
        if search:
            queryset = queryset.filter(name__contains=search)  #过滤条件用户名包含查询条件
        return queryset          #返回查询集列表


class APIGroupView(BaseAPIView):  #定义接口APIGroupView视图继承自基类视图BaseAPIView

    model = Group       #模块表Group

    def get_queryset(self):                                             #查询功能
        queryset = [i for i in self.model.objects.values('id', 'name')] #从数据库取出id,name放入查询集
        return queryset

    def get(self, request, *args, **kwargs):
        pk = kwargs.get('pk')                               #取id
        if pk:
            try:                                            #正常数据
                instance = self.model.objects.get(pk=pk)    #取出id对应的整条记录
                users = [{'id': user.id, 'username':user.username} for user in instance.user_set.all()] #查到用户集
                data = {
                    'id': instance.id,
                    'name': instance.name,
                    'users':users
                }
            except Exception as e:                        #如下情况触发异常
                data = e.args[0]                          #通常大多数异常类具有args属性，arg[0]是错误信息
            return JsonResponse({'data': data})           #返回get Json串，传参错误信息
        queryset = self.get_queryset()                    #获取所有查询集
        return JsonResponse({'count':len(queryset), 'data': queryset}) #返回Json串,查询集个数，查询集内容
