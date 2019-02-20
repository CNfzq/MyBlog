from django.db import models
from django.contrib.auth.models import AbstractUser,UserManager    #contrib是Django自带的应用，导入
# Create your models here.


class UserManager_Defined(UserManager):
    """
    自定义的UserManager_Defined类，继承重写create_superuser()方法
    """
    def create_superuser(self, username, password, email=None, **extra_fields):
        super().create_superuser(username=username, password=password, email=email, **extra_fields)


class Users(AbstractUser):
    """
    添加mobile,email_active字段到Django自带的User模型类，并继承AbstractUser类，使用父类自带的字段
    """
    mobile = models.CharField(max_length=11, unique=True, help_text='手机号', verbose_name='手机号',
        error_messages={
            'unique' : '此手机号已经注册'},)
    email_active = models.BooleanField(default=False,verbose_name='邮箱验证状态')
    REQUIRED_FIELDS = ['mobile']
    objects = UserManager_Defined()


    class Meta:
        db_table = 'tb_users'
        verbose_name = '用户'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username