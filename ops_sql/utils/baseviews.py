from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
#引入Paginator分页模块，EmptyPage空页面处理模块，PageNotAnInteger页数不为整数处理模块
from django.contrib.auth.mixins import LoginRequiredMixin
#基于类视图限制用户登录，导入LoginRequiredMixin提供登录状态验证，类函数会先检查用户是否登录，如是则继续访问否则退回登录页。
from django.views.generic import View, ListView
#通用视图引入View和ListView，ListView是在View基础上再做封装带分页效果
from django.shortcuts import render
#区别render回报提交页面, HttpResponse返回字符串, JsonResponse返回Json串
from django.http import QueryDict, JsonResponse
#引入QueryDict对象用来处理同一个键带有多个值，方法get()：根据键获取值,如果一个键同时拥有多个值将获取最后一个值,如果键不存在则返回None值,可以设置默认值进行后续处理
from utils.wrappers import handle_save_data
#调用自写wrappers装饰器,保证各个字段输入合法性,不会太长乱码异常格式等

class BaseListView(LoginRequiredMixin, ListView):   #定义基础带分页登录验证列表视图
    """"列表页/详情页, 增删改查, 通用类视图"""
    model = None            #无表
    template_detail = None  #无模板详细页
    paginate_by = 10         #分页间隔，10条数据为1页
    # Django内置分页器Paginator
    def handle_page(self, page, object_list):   #定义处理分页函数，page为页码，object_list当前页的对象列表
        paginator = Paginator(object_list, self.paginate_by, 1)  #Paginator分页器对象按每10条数据对象分页，获取前端请求取不到默认为1
        try:    #正常取值
            paginator_data = paginator.page(page)  #根据页码取出分页对象所属数据
        except PageNotAnInteger:                   #页码非整数触发异常
            paginator_data = paginator.page(1)     #传入第1页数据
        except EmptyPage:                          #页码不在有效范围内数据为空触发异常
            paginator_data = paginator.page(paginator.num_pages)  #传入总页数数据，即最后1页
        return paginator_data                      #返回查询到分页数据

    # HTTP中get请求，put修改，post创建，delete删除
    def get(self, request, *args, **kwargs):       #请求数据
        pk = kwargs.get('pk')                      #从字典取出id值，id在view中是关键字不能用，用pk代替
        if pk:
            try:                                   #正常取值
                instance = self.model.objects.get(pk=pk)   #取出id对应的整条记录
                return render(request, self.template_detail, instance.to_dict)  #返回前端页面和传参instance.to_dict
            except self.model.DoesNotExist:         #记录不存在触发异常
                return JsonResponse({'data': 'id {} not exits'.format(pk)})  #返回Json串，传参格式化后pk
        page = request.GET.get('page')              #取出页码
        search = self.request.GET.get('search', '') #search单独写函数, 前端页面传参内容做search,获取不到则为空
        queryset = self.get_queryset()            #取出记录集
        paginator_data = self.handle_page(page, queryset)  #对应页码的当页查询集
        return render(request, self.template_name, {'paginator_data': paginator_data, 'search': search})
        # 返回前端页面和传参字典，分页内容和查询条件

    # HTTP中get请求，put修改，post创建，delete删除
    @handle_save_data   #调用数据处理保存装饰器
    def post(self,request, *args, **kwargs):     #创建数据
        data = QueryDict(request.body).dict()    #从前端获取http.request的数据放到字典QueryDict
        self.model.objects.create(**data)        #将字典data创建到数据库
        return JsonResponse({'status': 1})       #返回状态码1 正常

    @handle_save_data   #调用装饰器
    def put(self, request, *args, **kwargs):    #修改数据
        pk = kwargs.get('pk')                   #取id值
        data = QueryDict(request.body).dict()   #从前端取到记录
        self.model.objects.filter(pk=pk).update(**data)  #查到id更新数据到数据库
        return JsonResponse({'status': 1})      #返回状态码1 正常

    def delete(self, request, *args, **kwargs):  #删除数据
        pk = kwargs.get('pk')                    #取id值
        instance = self.model.objects.get(pk=pk) #按id向数据库请求记录
        instance.delete()                        #删除该记录
        return JsonResponse({'status': 1})       #返回状态码1 正常


class BaseAPIView(View):                        #定义基础通用查询视图
    """"查询API, 通用类视图"""
    model = None                                #无表
    count_limit = 1000                          #最大行数1000

    def get_queryset(self):                     #查询数据
        queryset = self.model.objects.all()[:self.count_limit]   #向数据库查询所有记录，下标0~count_limit-1的记录
        qs = [i.to_dict for i in queryset]       #记录传入字典
        return qs                                #返回字典，即对应的记录集

    def get(self, request, *args, **kwargs):    #查询数据
        pk = kwargs.get('pk')                   #从字典取出pk值
        if pk:
            try:                                #正常取值
                instance = self.model.objects.get(pk=pk).to_dict   #取出id对应的整条记录
            except Exception as e:              #如下情况触发异常
                instance = e.args[0]            #通常大多数异常类具有args属性，arg[0]是错误信息
            return JsonResponse({'data': instance}) #返回Json串，传参错误信息
        queryset = self.get_queryset()          #获取所有查询集
        return JsonResponse({'count': len(queryset), 'data': queryset})  #返回Json串,查询集个数，查询集内容
