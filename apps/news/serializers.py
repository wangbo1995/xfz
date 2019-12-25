from rest_framework import serializers
from .models import News, NewsCategory, Comment, Banner
from apps.xfzauth.serializers import UserSerializer

class NewsCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsCategory
        fields = ('id', 'name')

class NewsSerializer(serializers.ModelSerializer):
    # category和author是外键，我们还需要进行一层序列化
    category = NewsCategorySerializer()
    author = UserSerializer()
    class Meta:
        model = News
        # 在首页新闻列表不需要获取新闻的正文，所以没有加上content
        fields = ('id', 'title', 'desc', 'thumbnail', 'pub_time', 'category', 'author')

class CommentSerizlizer(serializers.ModelSerializer):
    author = UserSerializer()
    class Meta:
        model = Comment
        fields = ('id', 'content', 'author', 'pub_time')

class BannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banner
        fields = ('id', 'image_url', 'priority', 'link_to')
