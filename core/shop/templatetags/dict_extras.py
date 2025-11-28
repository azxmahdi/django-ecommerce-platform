from django import template

register = template.Library()


@register.simple_tag
def get_feature_from_current_filters(current_filters, feature_id):
    return current_filters.get(f"feature_{feature_id}")
