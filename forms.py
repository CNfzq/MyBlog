import re

from django import forms
from django_redis import get_redis_connection
from django.contrib.auth import login
from django.db.models import Q
from users.models import Users
from verifications.constants import SMS_CODE_NUMS, USER_SESSION_EXPIRES


class RegisterForm(forms.Form):
    """
    register form data
    """
    username = forms.CharField(label='用户名', max_length=20, min_length=5,
                               error_messages={"min_length": "用户名长度要大于5", "max_length": "用户名长度要小于20",
                                               "required": "用户名不能为空"}
                               )
    password = forms.CharField(label='密码', max_length=20, min_length=6,
                               error_messages={"min_length": "密码长度要大于6", "max_length": "密码长度要小于20",
                                               "required": "密码不能为空"}
                               )
    password_repeat = forms.CharField(label='确认密码', max_length=20, min_length=6,
                                      error_messages={"min_length": "密码长度要大于6", "max_length": "密码长度要小于20",
                                                      "required": "密码不能为空"}
                                      )
    mobile = forms.CharField(label='手机号', max_length=11, min_length=11,
                             error_messages={"min_length": "手机号长度有误", "max_length": "手机号长度有误",
                                             "required": "手机号不能为空"})

    sms_code = forms.CharField(label='短信验证码', max_length=SMS_CODE_NUMS, min_length=SMS_CODE_NUMS,
                               error_messages={"min_length": "短信验证码长度有误", "max_length": "短信验证码长度有误",
                                               "required": "短信验证码不能为空"})
    # 单个字段需要返回值，需要return

    def clean_username(self):
        """
        check username
        """
        name = self.cleaned_data.get('username')
        if Users.objects.filter(username=name).exists():
            raise forms.ValidationError("用户名已存在，请重新输入！")

    def clean_mobile(self):
        """
        check mobile
        """
        tel = self.cleaned_data.get('mobile')
        if not re.match(r"^1[3-9]\d{9}$", tel):
            raise forms.ValidationError("手机号码格式不正确")

        if Users.objects.filter(mobile=tel).exists():         # exists()判断是否存在
            raise forms.ValidationError("手机号已注册，请重新输入！")

        return tel

    # 联合校验不需要返回值，不需要return，见官方源码
    def clean(self):
        """
        check password password_repeat and sms_code
        """
        cleaned_data = super().clean()

        # 1.获取参数
        passwd = cleaned_data.get('password')
        passwd_repeat = cleaned_data.get('password_repeat')
        tel = cleaned_data.get('mobile')
        sms_text = cleaned_data.get('sms_code')

        # 2.判断两次密码是否一致，不需要判断为空，字段已经判断了
        if passwd != passwd_repeat:
            raise forms.ValidationError("两次密码不一致")

        # 3.判断短信验证码是否正确，建立redis连接拿验证码
        redis_conn = get_redis_connection(alias='verify_codes')
        # 创建一个key,取值
        sms_fmt = "sms_{}".format(tel).encode('utf-8')
        real_sms = redis_conn.get(sms_fmt)
        if (not real_sms) or (sms_text != real_sms.decode('utf-8')):
            raise forms.ValidationError("短信验证码错误")


class LoginForm(forms.Form):
    """
    """
    user_account = forms.CharField(label='用户', required=True)
    password = forms.CharField(label='密码', max_length=20, min_length=6,
                               error_messages={"min_length": "密码长度要大于6", "max_length": "密码长度要小于20",
                                               "required": "密码不能为空"})
    remember_me = forms.BooleanField(required=False)

    def __init__(self, *args, **kwargs):
        """
        """
        self.request = kwargs.pop('request', None)
        super(LoginForm, self).__init__(*args, **kwargs)

    def clean_user_account(self):
        """
        """
        user_info = self.cleaned_data.get('user_account')
        if not user_info:
            raise forms.ValidationError("用户账号不能为空")

        if not re.match(r"^1[3-9]\d{9}$", user_info) and (len(user_info) < 5 or len(user_info) > 20):
            raise forms.ValidationError("用户账号格式不正确，请重新输入")

        return user_info

    def clean(self):
        """
        """
        cleaned_data = super().clean()
        # 获取用户账号
        user_info = cleaned_data.get('user_account')
        # 获取密码
        passwd = cleaned_data.get('password')
        hold_login = cleaned_data.get('remember_me')

        # 在form表单中实现登录逻辑
        user_queryset = Users.objects.filter(Q(mobile=user_info) | Q(username=user_info))
        if user_queryset:
            user = user_queryset.first()
            if user.check_password(passwd):
                if hold_login:  # redis中保存session信息
                    self.request.session.set_expiry(None)
                else:
                    self.request.session.set_expiry(USER_SESSION_EXPIRES)
                login(self.request, user)
            else:
                raise forms.ValidationError("密码不正确，请重新输入")

        else:
            raise forms.ValidationError("用户账号不存在，请重新输入")