import json
import logging

from django.shortcuts import render, redirect, reverse
from django.views import View
from django.contrib.auth import login, logout

from . forms import RegisterForm, LoginForm
from utils.json_fun import to_json_data
from utils.res_code import Code, error_map
from .models import Users


logger = logging.getLogger('django')

# Create your views here.


# 1.创建一个类视图
class RegisterView(View):
    """
    users register
    请求方法：POST
    url定义：/users/register/
    """
    # 2.定义get方法(渲染页面)
    def get(self, request):
        """
        处理get请求，渲染页面
        """
        return render(request, 'users/register.html')

    # 3.定义post方法(提交数据)
    def post(self, request):
        """
        处理post请求，提交数据
        """
        # 3-1.获取前端传过来的参数(前端传过来的数据可以是JSON格式的，XML格式的等其他格式)
        try:
            json_data = request.body     #body获取JSON数据,这里要捕获异常，接收JSON格式数据
            if not json_data:
                return to_json_data(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])
            dict_data = json.loads(json_data.decode('utf8'))
        except Exception as e:
            logger.info('错误信息：\n{}'.format(e))
            return to_json_data(errno=Code.UNKOWNERR, errmsg=error_map[Code.UNKOWNERR])
        # 3-2.校验参数(使用form表单进行校验，或者序列化serializers校验)，注意：data=参数接收的是字典，无论是form表单还是AJAX请求都要构造一个字典形式
        form = RegisterForm(data=dict_data)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            mobile = form.cleaned_data.get('mobile')
            # 3-3.将数据信息保存到数据库,create_user()方法见源码
            user = Users.objects.create_user(username=username, password=password, mobile=mobile)
            # 处理session登陆的信息
            login(request, user)
            return to_json_data(errmsg="恭喜您，注册成功！")
        else:
            # 3-4将结果返回前端
            # 定义一个错误信息列表，把所有的错误信息(form表单里面的)转化成字符串的形式
            err_msg_list = []
            for item in form.errors.get_json_data().values():
                err_msg_list.append(item[0].get('message'))
            err_msg_str = '/'.join(err_msg_list)

            return to_json_data(errno=Code.PARAMERR, errmsg=err_msg_str)


class LoginView(View):
    """
    用户登录
    """
    def get(self, request):
        return render(request, 'users/login.html')

    def post(self, request):
        json_data = request.body
        if not json_data:
            return to_json_data(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])
        # 将json转化为dict
        dict_data = json.loads(json_data.decode('utf8')) # 没有解码，会产生bug
        form = LoginForm(data=dict_data, request=request)
        if form.is_valid():
            return to_json_data(errmsg="恭喜您，登录成功！")
        else:
            # 定义一个错误信息列表
            err_msg_list = []
            for item in form.errors.get_json_data().values():
                err_msg_list.append(item[0].get('message'))
            err_msg_str = '/'.join(err_msg_list)  # 拼接错误信息为一个字符串

            return to_json_data(errno=Code.PARAMERR, errmsg=err_msg_str)


class LogoutView(View):
    """
    退出用户
    """
    def get(self, request):
        logout(request)
        return redirect(reverse("users:login"))




