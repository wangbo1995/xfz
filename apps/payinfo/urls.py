from django.urls import path
from . import views

app_name = 'payinfo'

urlpatterns = [
    path('', views.index, name='index'),
    path('payinfo_order/', views.payinfo_order, name='payinfo_order'),
    path('notify_url/', views.notify_view, name='notify_view'),
    path('download/', views.download, name='download')
]