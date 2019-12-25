from django import template
from apps.payinfo.models import PayinfoOrder

register = template.Library()

@register.filter
def is_buyed(payinfo, user):
    if user.is_authenticated:
        result = PayinfoOrder.objects.filter(payinfo=payinfo, buyer=user, status=2).exists()
        return result
    else:
        return False
