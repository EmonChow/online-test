
from django import template

register = template.Library()

@register.filter
def get_digit(list, index):
    try:
        return list[int(index)]
    except (IndexError, ValueError):
        return None