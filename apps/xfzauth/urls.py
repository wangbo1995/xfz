from django.urls import path
from . import views

app_name = 'xfzauth'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('img_chptcha/', views.img_chptcha, name='img_chptcha'),
    path('sms_captcha/', views.sms_captcha, name='sms_captcha'),
    path('register/', views.register, name='register')
]