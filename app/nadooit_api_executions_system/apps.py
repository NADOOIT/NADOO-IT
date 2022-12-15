# Author: Christoph Backhaus
# Date: 2022-10-30
# Version: 1.0.0
# Description: This is the app file for the nadooit app. It contains the urls for the app. From this file the urls are loaded into the main urls.py file.
# Compatibility: Django 4
# License: TBD

from django.apps import AppConfig


class NadooitApiExecutionsSystemConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "nadooit_api_executions_system"
