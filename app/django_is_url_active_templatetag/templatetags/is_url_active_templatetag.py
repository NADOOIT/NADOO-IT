#Author: Christoph Backhaus
#Date: 2022-10-30
#Version: 1.0.0
#Description: This is a custom template tag to check if a url is active or not. When the url is active, the class "active" is added to the html element.
#Compatibility: Django 4, Bootstrap 5
#License: TBD
#Usage: {% load is_url_active_templatetag %}
#       {% is_url_active request 'app_name:path_name' %}

from django.http import HttpRequest
from django.urls import reverse
from django import template

register = template.Library()


@register.simple_tag
def is_url_active(request:HttpRequest, url:str) -> str:
    # Main idea is to check if the url and the current path is a match
    if reverse(url) == request.path:
        return "active-link"

    print("url: ", url)
    print("request.path: ", request.path)

    if request.path in reverse(url) and len(request.path) > 1:
        return "active-link"

    return ""
