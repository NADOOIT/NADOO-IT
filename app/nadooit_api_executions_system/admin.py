from django.contrib import admin
from .models import *


# Register your models here.
class CustomerProgramExecutionAdmin(admin.ModelAdmin):
    list_display = [field.name for field in CustomerProgramExecution._meta.fields]


admin.site.register(CustomerProgramExecution, CustomerProgramExecutionAdmin)
admin.site.register(CustomerProgramExecutionManager)
