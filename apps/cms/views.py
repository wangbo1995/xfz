from django.core.paginator import Paginator
from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.views.generic import View
from django.views.decorators.http import require_POST, require_GET
from django.conf import settings
from django.utils.timezone import make_aware
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import permission_required
from django.contrib.auth import get_user_model
from apps.news.models import NewsCategory, News, Banner
from apps.news.serializers import BannerSerializer
from apps.xfzauth.decorators import xfz_login_required
from .forms import EditNewsCategoryForm, WriteNewsForm, AddBannerForm, EditBannerForm, EditNewsForm
from utils import restful
from datetime import datetime
from urllib import parse
import qiniu
import os

User = get_user_model()
LOGIN_URL = '/'

# 员工限制装饰器,必须is_staff=1,否则跳转至name=index的url视图上
@staff_member_required(login_url='index')
def index(request):
    return render(request, 'cms/index.html')

@method_decorator(permission_required(perm='news.change_news', login_url=LOGIN_URL), name='dispatch')
class NewsListView(View):
    def get(self, request):
        # request.GET：获取出来的所有数据，都是字符串类型，要转成int
        page = int(request.GET.get('p', 1))
        start = request.GET.get('start')
        end = request.GET.get('end')
        title = request.GET.get('title')
        # request.GET.get(参数,默认值)
        # 这个默认值是只有这个参数没有传递的时候才会使用
        # 如果传递了，但是是一个空的字符串，那么也不会使用默认值
        category_id = int(request.GET.get('category', 0))
        newses = News.objects.select_related('category', 'author')

        if start or end:
            if start:
                start_date = datetime.strptime(start, '%Y/%m/%d')
            else:
                start_date = datetime(year=2019, month=11, day=1)
            if end:
                end_date = datetime.strptime(end, '%Y/%m/%d')
            else:
                end_date = datetime.today()
            # 在当前的queryset基础上再根据时间范围filter
            newses = newses.filter(pub_time__range=(make_aware(start_date), make_aware(end_date)))

        if title:
            newses = newses.filter(title__icontains=title)

        if category_id:
            newses = newses.filter(category=category_id)

        # 每页5条数据
        paginator = Paginator(newses, 5)
        # 得到第page页对象
        page_obj = paginator.page(page)

        context_data = self.__get_pagination_data(paginator, page_obj)

        context = {
            'news_len': paginator.count,
            'categories': NewsCategory.objects.all(),
            # 得到当前page的数据
            'newses': page_obj.object_list,
            # 这两个参数一定要传到模板中
            'page_obj': page_obj,
            'paginator': paginator,
            'start': start,
            'end': end,
            'title': title,
            'category_id': category_id,
            # parse.urlencode方法将字典转换成url的查询字符串格式形如：a=1&b=2
            'url_query': '&' + parse.urlencode({
                # 如果为None则取or后面的值
                'start': start or '',
                'end': end or '',
                'title': title or '',
                'category': category_id or 0
            })
        }
        context.update(context_data)

        return render(request, 'cms/news_list.html', context=context)

    def __get_pagination_data(self, paginator, page_obj, around_count=2):
        current_page = page_obj.number
        # 总页数
        num_pages = paginator.num_pages
        # 当前页向左减去around_count后剩下的页数
        left_around_pages = current_page - 1 - around_count
        # 当前页向右减去around_count后剩下的页数
        right_around_pages = num_pages - current_page - around_count
        # 左边还有更多页
        left_has_more = False
        # 右边还有更多页
        right_has_more = False

        if left_around_pages <= 1:
            left_pages = range(1, current_page)
        else:
            left_has_more = True
            left_pages = range(left_around_pages, current_page)

        if right_around_pages <= 1:
            right_pages = range(current_page + 1, num_pages + 1)
        else:
            right_has_more = True
            right_pages = range(current_page + 1, current_page + around_count + 1)

        return {
            'left_pages': left_pages,
            'right_pages': right_pages,
            'current_page': current_page,
            'num_pages': num_pages,
            'left_has_more': left_has_more,
            'right_has_more': right_has_more
        }

@method_decorator(permission_required(perm="news.add_news", login_url=LOGIN_URL), name='dispatch')
class WriteNewsView(View):
    def get(self, request):
        categories = NewsCategory.objects.all()
        context = {
            'categories': categories,
        }
        return render(request, 'cms/write_news.html', context=context)

    def post(self, request):
        form = WriteNewsForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data.get('title')
            desc = form.cleaned_data.get('desc')
            thumbnail = form.cleaned_data.get('thumbnail')
            content = form.cleaned_data.get('content')
            category_id = form.cleaned_data.get('category')
            category = NewsCategory.objects.get(pk=category_id)
            News.objects.create(title=title, desc=desc, thumbnail=thumbnail, content=content, category=category,
                                author=request.user)
            return restful.ok()
        else:
            return restful.params_error(message=form.get_errors())

@method_decorator(permission_required(perm='news.change_news', login_url=LOGIN_URL), name='dispatch')
class EditNewsView(View):
    def get(self, request):
        news_id = request.GET.get('news_id')
        news = News.objects.get(pk=news_id)
        context = {
            'news': news,
            'categories': NewsCategory.objects.all()
        }
        return render(request, 'cms/write_news.html', context=context)

    def post(self, request):
        form = EditNewsForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data.get('title')
            desc = form.cleaned_data.get('desc')
            thumbnail = form.cleaned_data.get('thumbnail')
            content = form.cleaned_data.get('content')
            category_id = form.cleaned_data.get('category')
            pk = form.cleaned_data.get("pk")
            category = NewsCategory.objects.get(pk=category_id)
            News.objects.filter(pk=pk).update(title=title, desc=desc, thumbnail=thumbnail,
                                              content=content, category=category)
            return restful.ok()
        else:
            return restful.params_error(message=form.get_errors())

@method_decorator(xfz_login_required, name='dispatch')
class EditUserInfo(View):
    def get(self, request):
        return render(request, 'cms/user_info.html')

    def post(self, request):
        image_url = request.POST.get('image_url')
        desc = request.POST.get('desc')
        print(image_url, desc)
        user = request.user
        User.objects.filter(pk=user.pk).update(user_avater=image_url, user_desc=desc)
        return restful.ok()

@require_POST
@permission_required(perm="news.delete_news", login_url=LOGIN_URL)
def delete_news(request):
    news_id = request.POST.get('news_id')
    News.objects.filter(pk=news_id).delete()
    return restful.ok()

@require_GET
@permission_required(perm="news.change_newscategory", login_url=LOGIN_URL)
def news_category(request):
    categories = NewsCategory.objects.all()
    context = {
        'categories': categories,
    }
    return render(request, 'cms/news_category.html', context=context)

@require_POST
@permission_required(perm="news.add_newscategory", login_url=LOGIN_URL)
def add_news_category(request):
    name = request.POST.get('name')
    print(name)
    exist = NewsCategory.objects.filter(name=name).exists()
    if not exist:
        NewsCategory.objects.create(name=name)
        return restful.ok()
    else:
        return restful.params_error(message='该分类已经存在!')

@require_POST
@permission_required(perm="news.change_newscategory", login_url=LOGIN_URL)
def edit_news_category(request):
    print(request.POST)
    form = EditNewsCategoryForm(request.POST)
    if form.is_valid():
        pk = form.cleaned_data.get('pk')
        name = form.cleaned_data.get('name')

        exist = NewsCategory.objects.filter(name=name).exists()
        if exist:
            return restful.params_error(message='该分类已经存在!')
        try:
            # NewsCategory.objects.filter(pk=pk).update(name=name)
            category = NewsCategory.objects.filter(pk=pk)
            print(category)
            category.update(name=name)
            return restful.ok()
        except:
            return restful.params_error(message='该分类不存在！')
    else:
        return restful.params_error(message=form.get_errors())

@require_POST
@permission_required(perm="news.delete_newscategory", login_url=LOGIN_URL)
def delete_news_category(request):
    pk = request.POST.get('pk')
    print('id=', pk)
    try:
        # NewsCategory.objects.filter(pk=pk).delete()
        # 其实这种写法不用异常捕获，因为filter获取不到返回空的queryset,对空的queryset执行delete、update不会报错，相当于什么都没做
        category = NewsCategory.objects.filter(pk=pk)
        print(category)
        category.delete()
        return restful.ok()
    except:
        return restful.params_error(message='该分类不存在！')

@require_GET
@permission_required(perm="news.change_banner", login_url=LOGIN_URL)
def banners(request):
    return render(request,'cms/banners.html')

@require_GET
@permission_required(perm="news.view_banner", login_url=LOGIN_URL)
def banner_list(request):
    banners_ = Banner.objects.all()
    serialize = BannerSerializer(banners_, many=True)
    return restful.result(data=serialize.data)

@require_POST
@permission_required(perm="news.add_banner", login_url=LOGIN_URL)
def add_banner(request):
    form = AddBannerForm(request.POST)
    if form.is_valid():
        priority = form.cleaned_data.get('priority')
        image_url = form.cleaned_data.get('image_url')
        link_to = form.cleaned_data.get('link_to')
        banner = Banner.objects.create(priority=priority, image_url=image_url, link_to=link_to)
        return restful.result(data={"banner_id": banner.pk})
    else:
        return restful.params_error(message=form.get_errors())

@require_POST
@permission_required(perm="news.change_banner", login_url=LOGIN_URL)
def edit_banner(request):
    form = EditBannerForm(request.POST)
    if form.is_valid():
        pk = form.cleaned_data.get('pk')
        image_url = form.cleaned_data.get('image_url')
        link_to = form.cleaned_data.get('link_to')
        priority = form.cleaned_data.get('priority')
        Banner.objects.filter(pk=pk).update(image_url=image_url, link_to=link_to, priority=priority)
        return restful.ok()
    else:
        return restful.params_error(message=form.get_errors())

@require_POST
@permission_required(perm="news.delete_banner", login_url=LOGIN_URL)
def delete_banner(request):
    banner_id = request.POST.get('banner_id')
    Banner.objects.filter(pk=banner_id).delete()
    return restful.ok()

@require_POST
@staff_member_required(login_url='index')
def upload_file(request):
    file = request.FILES.get('file')
    name = file.name
    with open(os.path.join(settings.MEDIA_ROOT, name), 'wb') as fp:
        for chunk in file.chunks():
            fp.write(chunk)
    # 拥有域名+端口号，只需要传查询路径(路由)
    url = request.build_absolute_uri(settings.MEDIA_URL + name)
    return restful.result(data={'url': url})

@require_GET
@staff_member_required(login_url='index')
def qntoken(request):
    access_key = settings.QINIU_ACCESS_KEY
    secret_key = settings.QINIU_SECRET_KEY
    bucket = settings.QINIU_BUCKET_NAME

    q = qiniu.Auth(access_key, secret_key)
    token = q.upload_token(bucket)

    return restful.result(data={'token': token})
