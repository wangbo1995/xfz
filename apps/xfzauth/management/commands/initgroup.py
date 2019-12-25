from django.core.management.base import BaseCommand
from django.contrib.auth.models import ContentType, Permission, Group
from apps.news.models import News, NewsCategory, Banner, Comment
from apps.course.models import Course, CourseOrder, CourseCategory, Teacher
from apps.payinfo.models import Payinfo, PayinfoOrder

# 自定义命令的官方文档
# https://docs.djangoproject.com/en/2.0/howto/custom-management-commands/

# 自定义Django命令：
# 1、必须定义一个Command类并继承自BaseCommand，然后重写handle方法，在此方法中写你的逻辑
# 2、使用python manage.py <python文件名>执行，例如这里的：python manage.py initgroup
class Command(BaseCommand):
    def handle(self, *args, **options):
        # self.stdout.write(self.style.SUCCESS('hello'))
        # self.stdout.write(self.style.ERROR('hello'))

        # 1. 编辑组（管理新闻/管理课程/管理评论/管理轮播图等）
        edit_content_types = [
            ContentType.objects.get_for_model(News),
            ContentType.objects.get_for_model(NewsCategory),
            ContentType.objects.get_for_model(Banner),
            ContentType.objects.get_for_model(Comment),
            ContentType.objects.get_for_model(Course),
            ContentType.objects.get_for_model(CourseCategory),
            ContentType.objects.get_for_model(Teacher),
            ContentType.objects.get_for_model(Payinfo),
        ]
        edit_permissions = Permission.objects.filter(content_type__in=edit_content_types)
        # print(edit_content_types)
        editGroup = Group.objects.create(name='编辑')
        editGroup.permissions.set(edit_permissions)
        editGroup.save()
        self.stdout.write(self.style.SUCCESS('编辑组创建完成！'))

        # 2. 财务组（课程订单/付费资讯订单）
        finance_content_types = [
            ContentType.objects.get_for_model(CourseOrder),
            ContentType.objects.get_for_model(PayinfoOrder),
        ]
        finance_permissions = Permission.objects.filter(content_type__in=finance_content_types)
        financeGroup = Group.objects.create(name='财务')
        financeGroup.permissions.set(finance_permissions)
        financeGroup.save()
        self.stdout.write(self.style.SUCCESS('财务组创建完成！'))

        # 3. 管理员组（编辑组+财务组）
        admin_permissions = edit_permissions.union(finance_permissions)
        adminGroup = Group.objects.create(name='管理员')
        adminGroup.permissions.set(admin_permissions)
        adminGroup.save()
        # 4. 超级管理员，拥有所有的权限所以不需要创建分组
        self.stdout.write(self.style.SUCCESS('管理员组创建完成！'))
