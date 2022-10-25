from django.contrib import admin

from nadooit_program_ownership_system.models import NadooitCustomerProgram
from nadooit_program_ownership_system.models import NadooitCustomerProgramManager

# Register your models here.
admin.site.register(NadooitCustomerProgram)
admin.site.register(NadooitCustomerProgramManager)
