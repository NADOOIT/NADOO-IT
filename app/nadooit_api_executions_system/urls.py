# Author: Christoph Backhaus
# Date: 2022-10-30
# Version: 1.0.0
# Description: This is the urls file for the nadooit_api_executions_system. Here you can register urls for apis
# Compatibility: Django 4
# License: TBD

from django.urls import path

from nadooit_api_executions_system.views import create_execution, check_user

urlpatterns = [
    # path for the api requests for program executions
    path("executions", create_execution, name="create"),
    # path for the api requests for checking if a user is valid or not
    path("users/check", check_user, name="check"),
]
