from django import template

register = template.Library()

@register.filter
def split(value, sep):
    """Divide uma string usando um separador"""
    if value:
        return str(value).split(sep)
    return []

@register.filter
def join_with(value, separator):
    """Une uma lista com um separador"""
    if value and isinstance(value, list):
        return separator.join(str(item) for item in value)
    return value
