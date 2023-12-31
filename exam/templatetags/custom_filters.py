
from django import template

register = template.Library()

@register.filter
def get_digit(list, index):
    try:
        return list[int(index)]
    except (IndexError, ValueError):
        return None

@register.filter
def concat(value, arg):
    return f"{value}{arg}"    
    
    
@register.filter
def calculate_percentage(value, total):
    if total == 0:
        return 0
    return (value / total) * 100    