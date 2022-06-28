from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def render(value):
    if isinstance(value, bool):
        return mark_safe('&#10003;' if value else '&#10007;')
    return value
