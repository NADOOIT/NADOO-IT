from django.contrib import admin

from nadooit_hr.models import Employee
from nadooit_hr.models import EmployeeManager
from nadooit_hr.models import CustomerManager
from nadooit_hr.models import EmployeeContract

# Register your models here.
admin.site.register(Employee)
admin.site.register(EmployeeManager)
admin.site.register(CustomerManager)
admin.site.register(EmployeeContract)
