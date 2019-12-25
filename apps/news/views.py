from django.shortcuts import render
from django.db.models import Q
from django.http import Http404
from django.conf import settings
from .models import News, NewsCategory, Comment, Banner
from .forms import PublicCommentForm
from .serializers import NewsSerializer, CommentSerizlizer
from utils import restful
from apps.xfzauth.decorators import xfz_login_required

def index(request):
    # newses = News.objects.all()[0:2]
    # 当一个模型中有外键引用，可以使用select_related进行优化
    # 因为有外键，用以上方法在模板中获取分类名称和作者名会多两次查询，可以使用select_related进行性能优化，将外键中值一次全部查出来
    newses = News.objects.select_related('category', 'author').all()[0:2]
    categories = NewsCategory.objects.all()
    context = {
        'newses': newses,
        'categories': categories,
        'banners': Banner.objects.all()
    }

    return render(request, 'news/index.html', context=context)

def news_list(request):
    # 通过p参数，来指定要获取第几页的数据
    # 并且这个p参数，是通过查询字符串的方式传过来的/news/list/?p=2
    page = int(request.GET.get('p', 1))
    # 分类为0：代表提取所有新闻
    category_id = int(request.GET.get('category_id', 0))
    # 0,1
    # 2,3
    start = (page - 1) * settings.ONE_PAGE_NEWS_COUNT
    end = start + settings.ONE_PAGE_NEWS_COUNT

    if category_id == 0:
        # values()方法可以获取到字典，但是只能获取到外键的id，不能获取到分类和作者中的字段
        newses = News.objects.select_related('category', 'author').all()[start:end]
    else:
        newses = News.objects.select_related('category', 'author').filter(category__pk=category_id)[start:end]
        # 当字段是主键可以不写，直接写成下面这样
        # newses = News.objects.filter(category=category_id)
    # 我们可以用djangorestframework的序列化来解决这个问题，跟使用表单十分类似，many代表要序列多个值，因为newses中有多个值故设置成True
    serializer = NewsSerializer(newses, many=True)
    # 获取序列化后的数据
    data = serializer.data
    # print(type(data), data)
    # 使用json进行传输
    return restful.result(data=data)

def news_detail(request, news_id):
    try:
        # news = News.objects.select_related('category', 'author').get(pk=news_id)
        # 在模板中还会反向查询comment，我们可以使用prefetch_related进行优化
        # A模型反向查询模型B的时候使用prefetch_related进行优化，一共查询两次
        # 第一次是查询A模型（News）下的所有B模型（Comment），第二次是查询所有B模型下外键（comments__author）的字段
        news = News.objects.select_related('category', 'author').prefetch_related('comments__author').get(pk=news_id)
        context = {
            'news': news
        }
        return render(request, 'news/news_detail.html', context=context)
    except News.DoesNotExist:
        # Http404会返回templates中的404.html页面
        raise Http404

# 这里为什么不直接用django提供的login_required原因是：立即评论走的是ajax，所以login_required中的重定向功能用不了
# 所以我们自定义一个装饰器，比内置的login_required多处理ajax类型的请求！
@xfz_login_required
def public_comment(request):
    form = PublicCommentForm(request.POST)
    if form.is_valid():
        news_id = form.cleaned_data.get('news_id')
        content = form.cleaned_data.get('content')
        news = News.objects.get(pk=news_id)
        comment = Comment.objects.create(content=content, news=news, author=request.user)
        # 这里不需要使用many=True，因为comment仅为一条数据
        serizlize = CommentSerizlizer(comment)
        return restful.result(data=serizlize.data)
    else:
        return restful.params_error(message=form.get_errors())

def search(request):
    q = request.GET.get('q')
    # 判断是否有(字符串空或None)查询字符串q，有就是点击了查询，没有就是第一次进入搜索界面，展示热点新闻
    is_show_hot = True
    if q:
        newses = News.objects.select_related('category', 'author').filter(Q(title__icontains=q) | Q(content__icontains=q))
        is_show_hot = False
    else:
        newses = News.objects.select_related('category', 'author').filter(category=3)
    context = {
        'newses': newses,
        'is_show_hot': is_show_hot
    }

    return render(request, 'search/search1.html', context=context)
