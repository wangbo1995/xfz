from django.urls import path
from . import views, course_views, staff_views
from .views import NewsListView

app_name = 'cms'

urlpatterns = [
    path('', views.index, name='index'),
    path('news_list/', NewsListView.as_view(), name='news_list'),
    path('write_news/', views.WriteNewsView.as_view(), name='write_news'),
    path('edit_news/', views.EditNewsView.as_view(), name='edit_news'),
    path('edit_user/', views.EditUserInfo.as_view(), name='edit_user'),
    path('delete_news/', views.delete_news, name='delete_news'),
    path('news_category/', views.news_category, name='news_category'),
    path('add_news_category/', views.add_news_category, name='add_news_category'),
    path('edit_news_category/', views.edit_news_category, name='edit_news_category'),
    path('delete_news_category/', views.delete_news_category, name='delete_news_category'),
    path('banners/', views.banners, name='banners'),
    path('add_banner/', views.add_banner, name='add_banner'),
    path('delete_banner/', views.delete_banner, name='delete_banner'),
    path('edit_banner/', views.edit_banner, name='edit_banner'),
    path('banner_list/', views.banner_list, name='banner_list'),
    path('upload_file/', views.upload_file, name='upload_file'),
    path('qntoken/', views.qntoken, name='qntoken'),
]

# 这是课程相关的url映射
urlpatterns += [
    path('pub_course/', course_views.PubCourse.as_view(), name='pub_course')
]

# 员工管理
urlpatterns += [
    path('staffs/', staff_views.staffs_view, name='staffs'),
    path('add_staff/', staff_views.AddStaffView.as_view(), name='add_staff'),
    path('edit_staff/<staff_id>/', staff_views.editStaffView.as_view(), name='edit_staff'),
    path('delete_staff/<staff_id>/', staff_views.delete_staff, name='delete_staff')
]
