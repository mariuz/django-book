from django import template
from djangobook.rst import publish_html
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def rst(text):
    return mark_safe(publish_html(text)['body'])