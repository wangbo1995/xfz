#encoding: utf-8
from django import template
from datetime import datetime
from django.utils.timezone import now as now_func, localtime

register = template.Library()

@register.filter
def time_since(value):
    """
    time距离现在的时间间隔
    1.如果时间间隔小于1分钟以内，那么就显示“刚刚”
    2.如果是大于1分钟小于1小时，那么就显示“xx分钟前”
    3.如果是大于1小时小于24小时，那么就显示“xx小时前”
    4.如果是大于24小时小于30天以内，那么就显示“xx天前”
    5.否则就是显示具体的时间
    2017/10/20 16:15
    """
    if not isinstance(value, datetime):
        return value
    # django.utils.timezone.now()得到的是清醒的时间，value是我们存数据库中也是个清醒的时间，所以两种可以相减
    # 清醒的时间和幼稚的时间不能相减
    now = now_func()
    # timedelay.total_seconds
    timestamp = (now - value).total_seconds()
    if timestamp < 60:
        return '刚刚'
    elif timestamp >= 60 and timestamp < 60*60:
        minutes = int(timestamp/60)
        return '%s分钟前' % minutes
    elif timestamp >= 60*60 and timestamp < 60*60*24:
        hours = int(timestamp/60/60)
        return '%s小时前' % hours
    elif timestamp >= 60*60*24 and timestamp < 60*60*24*30:
        days = int(timestamp/60/60/24)
        return '%s天前' % days
    else:
        return value.strftime("%Y/%m/%d %H:%M")

@register.filter
def time_format(value):
    if not isinstance(value, datetime):
        return value
    # 数据库拿出来的时间是UTC的，可以使用django.utils.timezone.localtime将其转换成setting.py设置的时区时间
    return localtime(value).strftime("%Y/%m/%d %H:%M:%S")

@register.filter
def author_other_newses(news):
    newses = news.author.news_set.exclude(pk=news.pk)

    return newses
