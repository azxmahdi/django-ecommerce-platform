from django import template
from django.urls import reverse

register = template.Library()


@register.simple_tag(takes_context=True)
def active_link(context, view_name, *args, **kwargs):
    request = context["request"]
    try:
        url = reverse(view_name, args=args, kwargs=kwargs)
    except Exception:
        url = None

    return "active" if url and request.path == url else ""
