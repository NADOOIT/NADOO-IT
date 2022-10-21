from django.contrib import admin

from nadooit_time_account.models import (
    CustomerTimeAccount,
    TimeAccount,
    EmployeeTimeAccount,
    WorkTimeAccountEntry,
    TimeAccountManager,
)

# Register your models here.
admin.site.register(TimeAccount)
admin.site.register(EmployeeTimeAccount)
admin.site.register(WorkTimeAccountEntry)
admin.site.register(CustomerTimeAccount)
admin.site.register(TimeAccountManager)
