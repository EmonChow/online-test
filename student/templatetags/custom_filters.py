
from django import template

from exam.models import Result

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
    


@register.filter(name='get_answer')
def get_answer(question_id, results):
    try:
        result = results.get(exam__id=question_id)
        return result.answer
    except Result.DoesNotExist:
        return "" 
    
@register.filter
def calculate_percentage(value, total):
    if total == 0:
        return 0
    return (value / total) * 100    