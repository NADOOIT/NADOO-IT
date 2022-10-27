from django.contrib import admin

from nadooit_hr.models import Employee
from nadooit_hr.models import EmployeeManager

# Register your models here.
admin.site.register(Employee)
admin.site.register(EmployeeManager)
