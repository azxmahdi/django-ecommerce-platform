from django import template
from django.utils import timezone

register = template.Library()


@register.filter
def remaining_minutes(value):
    if hasattr(value, "order_by"):
        payment = value.order_by("-created_date").first()
        if not payment or not hasattr(payment, "expired_date"):
            return 0
        expired_date = payment.expired_date

    elif isinstance(value, timezone.datetime.__class__):
        expired_date = value + timezone.timedelta(minutes=11)

    else:
        return 0

    now = timezone.now()
    remaining = expired_date - now
    minutes = int(remaining.total_seconds() // 60)
    return minutes if minutes > 0 else 0
