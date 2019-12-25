from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from shortuuidfield import ShortUUIDField
from django.db.utils import IntegrityError

class UserManager(BaseUserManager):
    def _create_user(self, telephone, username, password, **kwargs):
        if not telephone:
            raise ValueError('手机号不能为空！')
        if not username:
            raise ValueError('用户名不能为空！')
        if not password:
            raise ValueError('密码不能为空！')

        user = self.model(telephone=telephone, username=username, **kwargs)
        user.set_password(password)
        user.save()

        return user

    def create_user(self, telephone, username, password, **kwargs):
        kwargs['is_superuser'] = False
        return self._create_user(telephone=telephone, username=username, password=password, **kwargs)

    def create_superuser(self, telephone, username, password, **kwargs):
        kwargs['is_superuser'] = True
        kwargs['is_staff'] = True
        return self._create_user(telephone=telephone, username=username, password=password, **kwargs)

class User(AbstractBaseUser, PermissionsMixin):
    uid = ShortUUIDField(primary_key=True)
    telephone = models.CharField(max_length=11, unique=True)
    # 设置可以为空，不然创建User的时候不填email，Django默认传一个空字符串
    email = models.EmailField(unique=True, null=True)
    username = models.CharField(max_length=32)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    data_joined = models.DateTimeField(auto_now_add=True)
    # 用户头像
    user_avater = models.URLField(null=True)
    # 个人简介
    user_desc = models.CharField(max_length=32)

    USERNAME_FIELD = 'telephone'
    REQUIRED_FIELDS = ['username']
    # 给指定用户发送邮件，是根据这个字段，用处不是很大
    EMAIL_FIELD = 'email'

    objects = UserManager()

    def get_full_name(self):
        return self.username

    def get_short_name(self):
        return self.username
