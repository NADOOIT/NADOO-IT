from django.contrib import admin

from nadooit_hr.models import Employee
from nadooit_hr.models import EmployeeContract
from nadooit_hr.models import EmployeeManagerContract
from nadooit_hr.models import CustomerManagerContract
from nadooit_hr.models import CustomerProgramManagerContract
from nadooit_hr.models import CustomerProgramExecutionManagerContract
from nadooit_hr.models import TimeAccountManagerContract


# Register your models here.
admin.site.register(Employee)

admin.site.register(CustomerManagerContract)
admin.site.register(CustomerProgramManagerContract)
admin.site.register(CustomerProgramExecutionManagerContract)

admin.site.register(TimeAccountManagerContract)

admin.site.register(EmployeeContract)
admin.site.register(EmployeeManagerContract)
