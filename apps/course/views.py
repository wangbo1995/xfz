from django.shortcuts import render, redirect, reverse
from .models import Course, CourseOrder
import time, hmac, os, hashlib
from django.conf import settings
from utils import restful
from hashlib import md5
from apps.xfzauth.decorators import xfz_login_required
from django.views.decorators.csrf import csrf_exempt

def index(request):
    context = {
        'courses': Course.objects.all()
    }
    return render(request, 'course/course_index.html', context=context)

@xfz_login_required
def course_detail(request, course_id):
    course = Course.objects.get(pk=course_id)
    courses = Course.objects.exclude(pk=course_id)[0:3]
    user = request.user
    buyed = CourseOrder.objects.filter(course=course, buyer=user, status=2).exists()
    context = {
        'course': course,
        'buyed': buyed,
        'courses': courses
    }
    return render(request, 'course/course_detail.html', context=context)

def course_token(request):
    # video：是视频文件的完整链接
    file = request.GET.get('video')

    course_id = request.GET.get('course_id')
    if not CourseOrder.objects.filter(course_id=course_id, buyer=request.user, status=2).exists():
        return restful.params_error(message='请先购买课程！')

    expiration_time = int(time.time()) + 2 * 60 * 60

    USER_ID = settings.BAIDU_CLOUD_USER_ID
    USER_KEY = settings.BAIDU_CLOUD_USER_KEY

    # file=http://hemvpc6ui1kef2g0dd2.exp.bcevod.com/mda-igjsr8g7z7zqwnav/mda-igjsr8g7z7zqwnav.m3u8
    extension = os.path.splitext(file)[1]
    media_id = file.split('/')[-1].replace(extension, '')

    # unicode->bytes=unicode.encode('utf-8')bytes
    # Python3定义字符串的编码是Unicode，用.encode('utf-8')可转成bytes
    key = USER_KEY.encode('utf-8')
    message = '/{0}/{1}'.format(media_id, expiration_time).encode('utf-8')
    signature = hmac.new(key, message, digestmod=hashlib.sha256).hexdigest()
    token = '{0}_{1}_{2}'.format(signature, USER_ID, expiration_time)
    return restful.result(data={'token': token})

@xfz_login_required
def course_order(request, course_id):
    course = Course.objects.get(pk=course_id)
    order = CourseOrder.objects.create(course=course, buyer=request.user, status=1, amount=course.price)
    context = {
        'goods': {
            'thumbnail': course.cover_url,
            'title': course.title,
            'price': course.price
        },
        'order': order,
        # /course/notify_url/
        'notify_url': request.build_absolute_uri(reverse('course:notify_view')),
        'return_url': request.build_absolute_uri(reverse('course:course_detail', kwargs={"course_id": course.pk}))
    }
    return render(request, 'course/course_order.html', context=context)
    # return render(request, 'course/course_order.html', context={'course': course})

@xfz_login_required
def course_order_key(request):
    goodsname = request.POST.get("goodsname")
    istype = request.POST.get("istype")
    notify_url = request.POST.get("notify_url")
    orderid = request.POST.get("orderid")
    price = request.POST.get("price")
    return_url = request.POST.get("return_url")

    # paysapi info
    token = ''
    uid = ''
    orderuid = str(request.user.pk)

    print('goodsname:',goodsname)
    print('istype:',istype)
    print('notify_url:',notify_url)
    print('orderid:',orderid)
    print('price:',price)
    print('return_url:',return_url)

    key = md5((goodsname + istype + notify_url + orderid + orderuid + price + return_url + token + uid).encode(
        "utf-8")).hexdigest()
    return restful.result(data={"key": key})

# 这个装饰器用于赦免视图绕过django的csrf验证
@csrf_exempt
def notify_view(request):
    orderid = request.POST.get('orderid')
    print('='*10)
    print(orderid)
    print('='*10)
    CourseOrder.objects.filter(pk=orderid).update(status=2)
    return restful.ok()
