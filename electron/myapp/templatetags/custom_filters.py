# myapp/templatetags/custom_filters.py
from django import template


register = template.Library()


@register.filter
def get(dictionary, key):
       """Custom filter to get a value from a dictionary by key."""
       return dictionary.get(key)