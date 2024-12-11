from django import template

register = template.Library()

@register.filter
def multiply(value, arg):
    """Multiply the value by the arg."""
    try:
        return value * arg
    except (TypeError, ValueError):
        return 0
