# Author: Christoph Backhaus
# Date: 2022-10-30
# Version: 1.0.0
# Compatibility: Django 4
# License: TBD

from django.contrib import admin

from .models import *

# Register your models here.
admin.site.register(User)
