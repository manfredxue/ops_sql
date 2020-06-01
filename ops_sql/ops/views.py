# coding=utf-8
from django.views.generic import View, TemplateView             #View基于类视图，改造通用类视图成TemplateView get带传参data
from django.contrib.auth import authenticate, login, logout     #导入authenticate, login, logout模块
from django.http import HttpResponseRedirect                    #Http逻辑处理后转到其他页面修改再重定向到前端
from django.http.response import JsonResponse                   #后端获取前段数据放在QueryDict集中,JsonResponse返回Json格式
from django.contrib.auth.mixins import LoginRequiredMixin       #验证登录用户类型和权限


class LoginView(TemplateView):                                #登录处理视图
    """登录页面, 用户密码鉴权"""
    template_name = 'login.html'                               #模板即前端文件，根目录为templates/下, login登录验证页
    # HTTP中get请求，put修改，post创建，delete删除
    def post(self, request):                                   #创建数据
        username = request.POST.get('username', None)
        password = request.POST.get('password', None)
        user = authenticate(username=username, password=password)  # django鉴权
        if user is not None:  # 用户密码及token正确
            login(request, user)  #用户登录转向登录页
            status = 0        #状态0正常
        else:
            status = 1        #状态1错误
        return JsonResponse({'status': status})  #返回状态值


class LogoutView(LoginRequiredMixin, View):                     #登出处理视图，函数会先检查用户是否登录，如是则继续访问，否则退回登录页。
    """"退出登录"""
    def get(self, request):                                     #查询数据
        logout(request)                                         #退出登录
        return HttpResponseRedirect("/login/")                  #再重定向到登入界面


class IndexPage(LoginRequiredMixin, TemplateView):              #登入处理

    template_name = 'index.html'                                #首页
