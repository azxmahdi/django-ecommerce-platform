from django import template
from django.utils import timezone

register = template.Library()


@register.filter
def format_time(datetime_obj):

    if datetime_obj:
        if timezone.is_aware(datetime_obj):
            datetime_obj = timezone.localtime(datetime_obj)

        return datetime_obj.strftime("%H : %M")
    return ""
