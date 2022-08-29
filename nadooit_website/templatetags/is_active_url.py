from cgi import print_form
from django.urls import reverse
from django import template

register = template.Library()


@register.simple_tag
def is_active_url(request, url):
    # Main idea is to check if the url and the current path is a match
    if reverse(url) == request.path:
        return "active-url"

    if request.path in reverse(url) and len(request.path) > 1:
        return "active-url"

    return ""
