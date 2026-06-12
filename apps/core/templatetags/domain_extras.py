from django import template

register = template.Library()


@register.filter
def dict_get(mapping, key):
    """Look up ``mapping[key]`` from a template, falling back to the key."""
    if isinstance(mapping, dict):
        return mapping.get(key, key)
    return key
