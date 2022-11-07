# Author: Christoph Backhaus
# Date: 2022-10-30
# Version: 1.0.0
# Description: This is the admin page for the nadooit_api_executions_system. Here you can register models that will then be shown on the admin page.
# Compatibility: Django 4
# License: TBD

from django.contrib import admin
from .models import *


# Register your models here.
admin.site.register(CustomerProgramExecution)
