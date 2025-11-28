import jdatetime
from django import template

register = template.Library()


@register.filter
def jalali_date(value):

    if not value:
        return ""
    date = jdatetime.date.fromgregorian(date=value.date())
    months = [
        "فروردین",
        "اردیبهشت",
        "خرداد",
        "تیر",
        "مرداد",
        "شهریور",
        "مهر",
        "آبان",
        "آذر",
        "دی",
        "بهمن",
        "اسفند",
    ]
    month_name = months[date.month - 1]
    return f"{date.day} / {month_name} / {date.year}"
