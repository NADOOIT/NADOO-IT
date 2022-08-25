from django.db import models
import uuid

from nadooit_program_ownership_system.models import NadooitCustomerProgram

# Create your models here.


class CustomerProgramExecution(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    program_time_saved_in_seconds = models.IntegerField(default=0)
    customer_program = models.ForeignKey(NadooitCustomerProgram, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=True)
    updated_at = models.DateTimeField(auto_now=True, editable=True)

    def __str__(self):
        return self.customer_program.program.name
