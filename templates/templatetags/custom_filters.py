from django import template

register = template.Library()


@register.filter(name='replace')
def replace(value, args):
    """Replace occurrences of a string with another string."""
    old, new = args.split(',')
    return value.replace(old.strip(), new.strip())
