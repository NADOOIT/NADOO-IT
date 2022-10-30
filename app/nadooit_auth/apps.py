#Author: Christoph Backhaus
#Date: 2022-10-30
#Version: 1.0.0
#Compatibility: Django 4
#License: TBD
from django.apps import AppConfig


class AuthConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'nadooit_auth'
