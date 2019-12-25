from django.shortcuts import render, redirect, reverse
from apps.xfzauth.models import User
from django.views.generic import View
from django.contrib.auth.models import Group
from apps.xfzauth.decorators import xfz_superuser_required
from django.views.decorators.http import require_GET
from django.utils.decorators import method_decorator
from django.contrib import messages
from utils import restful

@xfz_superuser_required
def staffs_view(request):
    staffs = User.objects.filter(is_staff=True)
    context = {
        'staffs': staffs
    }
    return render(request, 'cms/staffs.html', context=context)

@method_decorator(xfz_superuser_required, name='dispatch')
class AddStaffView(View):
    def get(self, request):
        groups = Group.objects.all()
        context = {
            'groups': groups
        }
        return render(request, 'cms/add_staff.html', context=context)

    def post(self, request):
        telephone = request.POST.get('telephone')
        user = User.objects.filter(telephone=telephone).first()
        if user:
            user.is_staff = True
            # 因为checkbox上的name都叫groups，我们需要用getlit方法获取全部，而用get只能获取到其中一个
            group_ids = request.POST.getlist("groups")
            groups = Group.objects.filter(pk__in=group_ids)
            # 将该用户的组重新设置成groups中的组
            user.groups.set(groups)
            user.save()
            return redirect(reverse('cms:staffs'))
        else:
            messages.info(request, '该手机号码不存在！')
            return redirect(reverse('cms:add_staff'))

@method_decorator(xfz_superuser_required, name='dispatch')
class editStaffView(View):
    def get(self, request, staff_id):
        user = User.objects.filter(pk=staff_id).first()
        if user:
            groups = Group.objects.all()
            user_groups = user.groups.all()
            context = {
                'telephone': user.telephone,
                'groups': groups,
                'user_groups': user_groups
            }
            return render(request, 'cms/edit_staff.html', context=context)
        else:
            return restful.params_error(message= '员工{}不存在！'.format(staff_id))

    def post(self, request, staff_id):
        telephone = request.POST.get('telephone')
        user = User.objects.filter(telephone=telephone).first()
        if user:
            # 因为checkbox上的name都叫groups，我们需要用getlit方法获取全部，而用get只能获取到其中一个
            group_ids = request.POST.getlist("groups")
            groups = Group.objects.filter(pk__in=group_ids)
            # 将该用户的组重新设置成groups中的组
            user.groups.set(groups)
            user.save()
            return redirect(reverse('cms:staffs'))
        else:
            messages.info(request, '该手机号码不存在！')
            return redirect(reverse('cms:edit_staff'))

@require_GET
@xfz_superuser_required
def delete_staff(request, staff_id):
    user = User.objects.filter(pk=staff_id).first()
    if user:
        user.is_staff = False
        user.save()
        return redirect(reverse('cms:staffs'))
    else:
        return restful.params_error(message='员工{}不存在！'.format(staff_id))
