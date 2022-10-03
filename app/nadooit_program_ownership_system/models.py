import uuid
from django.db import models
from nadooit_crm.models import Customer
from nadooit_program.models import NadooitProgram
from nadooit_time_account.models import TimeAccount

# Create your models here.


class NadooitProgramShare(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    share_of = models.ForeignKey(NadooitProgram, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=True)
    updated_at = models.DateTimeField(auto_now=True, editable=True)

    def __str__(self):
        return self.id


class NadooitCustomerProgram(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    program_time_saved_per_execution_in_seconds = models.IntegerField(default=0)
    time_account = models.ForeignKey(TimeAccount, on_delete=models.SET_NULL, null=True)
    over_charge = models.BooleanField(default=False)
    program = models.ForeignKey(NadooitProgram, on_delete=models.SET_NULL, null=True)
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=True)
    updated_at = models.DateTimeField(auto_now=True, editable=True)

    def __str__(self):
        return str(self.id) + " " + self.program.name
