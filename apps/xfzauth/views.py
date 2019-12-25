from django.contrib.auth import login, logout, authenticate
from django.views.decorators.http import require_POST
from django.shortcuts import render, redirect, reverse
from django.http import HttpResponse
from utils.aliyunsdk import aliyunsms
from utils.captcha.xfzcaptcha import Captcha
from utils import restful
from .forms import LoginForm, RegisterFrom
from io import BytesIO
from django.db.utils import IntegrityError
from django.core.cache import cache
import django_redis
from django.contrib.auth import get_user_model

User = get_user_model()
# CACHE = django_redis.get_redis_connection()

@require_POST
def login_view(request):
    form = LoginForm(request.POST)
    if form.is_valid():
        telephone = form.cleaned_data.get('telephone')
        password = form.cleaned_data.get('password')
        remember = form.cleaned_data.get('remember')
        # 我们重写了User并指定了username为telephone
        user = authenticate(request, username=telephone, password=password)
        if user:
            if user.is_active:
                login(request, user)
                if remember:
                    # 两周
                    request.session.set_expiry(None)
                else:
                    # 退出浏览器时清除登录session
                    request.session.set_expiry(0)
                return restful.ok()
            else:
                return restful.auth_error(message='该用户权限被冻结！')
        else:
            return restful.params_error(message='手机号或者密码错误！')
    else:
        return restful.params_error(message=form.get_errors())

def logout_view(request):
    logout(request)
    return redirect(reverse('index'))

@require_POST
def register(request):
    form = RegisterFrom(request.POST)
    if form.is_valid():
        telephone = form.cleaned_data.get('telephone')
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password1')

        user = User.objects.create_user(telephone=telephone, username=username, password=password)

        login(request, user)
        return restful.ok()
    else:
        print(form.get_errors())
        return restful.params_error(form.get_errors())

def img_chptcha(request):
    text, image = Captcha.gene_code()
    # BytesIO：相当于一个管道，用来存储图片的流数据
    out = BytesIO()
    # 调用image的save方法，将这个image对象保存到BytesIO中
    image.save(out, 'png')
    # 将BytesIO的文件指针移动到最开始的位置
    out.seek(0)

    response = HttpResponse(content_type='image/png')
    # 从BytesIO的管道中，读取出图片数据，保存到response对象上
    response.write(out.read())
    # 上一句out.read()执行完之后，指针走到文件最后的位置，那么out.tell()是获取当前位置，自然就是文件的大小（字节数）
    response['Content-length'] = out.tell()

    # 12Df：12Df.lower()
    cache.set(text.lower(), text.lower(), 5*60)
    # CACHE.set(text.lower(), text.lower(), ex=5*60)

    return response

def sms_captcha(request):
    # /sms_captcha/?telephone=xxx
    telephone = request.GET.get('telephone')
    code = Captcha.gene_text()
    cache.set(telephone, code, 5*60)
    # CACHE.set(telephone, code, ex=5*60)
    print('短信验证码：', code)
    # result = smssender.send(telephone, code)
    result = aliyunsms.send_sms(telephone, code)
    # result = True
    if result:
        return restful.ok()
    else:
        return restful.params_error(message="短信验证码发送失败！")
