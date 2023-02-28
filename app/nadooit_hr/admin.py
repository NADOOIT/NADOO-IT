from django.contrib import admin
from nadooit_hr.models import (CustomerManagerContract,
                               CustomerProgramExecutionManagerContract,
                               CustomerProgramManagerContract, Employee,
                               EmployeeContract, EmployeeManagerContract,
                               TimeAccountManagerContract)

# Register your models here.
admin.site.register(Employee)

admin.site.register(CustomerManagerContract)
admin.site.register(CustomerProgramManagerContract)
admin.site.register(CustomerProgramExecutionManagerContract)

admin.site.register(TimeAccountManagerContract)

admin.site.register(EmployeeContract)
admin.site.register(EmployeeManagerContract)
