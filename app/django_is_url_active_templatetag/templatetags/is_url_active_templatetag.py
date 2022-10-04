from django.urls import reverse
from django import template

register = template.Library()


@register.simple_tag
def is_url_active(request, url):
    # Main idea is to check if the url and the current path is a match
    if reverse(url) == request.path:
        return "active-url"

    print("url: ", url)
    print("request.path: ", request.path)

    if request.path in reverse(url) and len(request.path) > 1:
        return "active-url"

    return ""
