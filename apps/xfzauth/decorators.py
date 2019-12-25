from utils import restful
from django.shortcuts import redirect
from functools import wraps
from django.http import Http404

def xfz_login_required(func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            return func(request, *args, **kwargs)
        else:
            if request.is_ajax():
                return restful.auth_error(message='请先登录！')
            else:
                return redirect('/')

    return wrapper

def xfz_superuser_required(viewfunc):
    @wraps(viewfunc)
    def decorator(request, *args, **kwargs):
        if request.user.is_superuser:
            return viewfunc(request, *args, **kwargs)
        else:
            raise Http404()
    return decorator
