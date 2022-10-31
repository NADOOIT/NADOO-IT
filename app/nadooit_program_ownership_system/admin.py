from django.contrib import admin

from nadooit_program_ownership_system.models import CustomerProgram
from nadooit_program_ownership_system.models import CustomerProgramManager

# Register your models here.
admin.site.register(CustomerProgram)
admin.site.register(CustomerProgramManager)
