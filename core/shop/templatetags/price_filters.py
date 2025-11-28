from django import template

register = template.Library()


@register.filter(name="format_price")
def format_price(value):

    try:
        number = int(value)
        return "{:,}".format(number)
    except (ValueError, TypeError):
        return value
