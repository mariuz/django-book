from django import template
from djangobook.rst import publish_html

register = template.Library()

@register.filter
def rst(text):
    return publish_html(text)['body']