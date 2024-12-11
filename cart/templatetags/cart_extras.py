from django import template

register = template.Library()

@register.filter
def multiply(value, arg):
    """Multiply two numbers."""
    try:
        return value * arg
    except (ValueError, TypeError):
        return 0
