from django.contrib import admin

from nadooit_time_account.models import (
    CustomerNadooitTimeAccount,
    TimeAccount,
    TimeAccountEmployee,
    WorkTimeAccountEntry,
)

# Register your models here.
admin.site.register(TimeAccount)
admin.site.register(TimeAccountEmployee)
admin.site.register(WorkTimeAccountEntry)
admin.site.register(CustomerNadooitTimeAccount)
