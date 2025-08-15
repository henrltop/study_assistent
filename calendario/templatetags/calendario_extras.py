from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Template filter para acessar items de um dict com chave dinâmica"""
    if dictionary and key:
        return dictionary.get(key, [])
    return []

@register.filter 
def lookup(dictionary, key):
    """Template filter para acessar valores de dict por chave"""
    if dictionary is None:
        return []
    return dictionary.get(key, [])

@register.filter
def split(value, delimiter):
    """Template filter para dividir string por delimitador"""
    if value:
        return value.split(delimiter)
    return []

@register.filter
def stringformat(value, format_spec):
    """Template filter para formatar strings com formato específico"""
    try:
        return format_spec % value
    except (TypeError, ValueError):
        return value
