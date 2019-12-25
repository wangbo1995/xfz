from django import forms
from apps.form import FormMixin
from django.core.cache import cache
from django.contrib.auth import get_user_model
import django_redis

User = get_user_model()
# CACHE = django_redis.get_redis_connection()

class LoginForm(forms.Form, FormMixin):
    telephone = forms.CharField(max_length=11, min_length=11, error_messages={
        'max_length': '手机号长度应该为11位！',
        'min_length': '手机号长度应该为11位！',
        'required': '手机号不能为空！'
    })
    password = forms.CharField(max_length=20, min_length=6, error_messages={
        'max_length': '密码最大长度为20位！',
        'min_length': '密码最小长度为6位！',
        'required': '密码不能为空！'
    })
    remember = forms.IntegerField(required=False)

class RegisterFrom(forms.Form, FormMixin):
    telephone = forms.CharField(max_length=11, min_length=11, error_messages={
        'max_length': '手机号长度应该为11位！',
        'min_length': '手机号长度应该为11位！',
        'required': '手机号不能为空！'
    })
    username = forms.CharField(max_length=20, error_messages={
        'required': '用户名不能为空！'
    })
    password1 = forms.CharField(max_length=20, min_length=6, error_messages={
        'max_length': '密码最大长度为20位！',
        'min_length': '密码最小长度为6位！',
        'required': '密码不能为空！'
    })
    password2 = forms.CharField(max_length=20, min_length=6, error_messages={
        'max_length': '密码最大长度为20位！',
        'min_length': '密码最小长度为6位！',
        'required': '密码不能为空！'
    })
    img_captcha = forms.CharField(max_length=4, min_length=4, error_messages={
        'required': '图形验证码不能为空！'
    })
    sms_captcha = forms.CharField(max_length=4, min_length=4, error_messages={
        'required': '短信验证码不能为空！'
    })

    def clean(self):
        # 注意：进入clean方法的都是到目前为止没有问题的字段，有问题的字段不会在里面，所有你直接获取这个字段（字典中不存在的字段），得到的是none，
        cleaned_data = super(RegisterFrom, self).clean()
        telephone = cleaned_data.get('telephone')
        exists = User.objects.filter(telephone=telephone).exists()
        if exists:
            raise forms.ValidationError('该手机号已经被注册！')

        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        if password1 != password2:
            raise forms.ValidationError('两次密码输入不一致！')

        img_captcha = cleaned_data.get('img_captcha')
        if img_captcha:
            img_captcha_lower = img_captcha.lower()
            cached_img_captcha = cache.get(img_captcha_lower)
            # redis取出来的是bytes,要转成str
            # cached_img_captcha = str(CACHE.get(img_captcha_lower), encoding='utf-8')
            print(cached_img_captcha)
            if cached_img_captcha and cached_img_captcha.lower() != img_captcha_lower:
                raise forms.ValidationError("图形验证码错误！")

        sms_captcha = cleaned_data.get('sms_captcha')
        if sms_captcha and telephone:
            cached_sms_captcha = cache.get(telephone)
            # cached_sms_captcha = str(CACHE.get(telephone), encoding='utf-8')
            print(cached_sms_captcha)
            if cached_sms_captcha and cached_sms_captcha.lower() != sms_captcha.lower():
                raise forms.ValidationError('短信验证码错误！')

        return cleaned_data
