from django.db import models
import uuid

from nadooit_program_ownership_system.models import NadooitCustomerProgram

from django.dispatch import receiver

# Create your models here.


class CustomerProgramExecution(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    program_time_saved_in_seconds = models.IntegerField(default=0)
    customer_program = models.ForeignKey(NadooitCustomerProgram, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=True)
    updated_at = models.DateTimeField(auto_now=True, editable=True)

    def __str__(self):
        return self.customer_program.program.name

@receiver(models.signals.post_save, sender=CustomerProgramExecution)
def cutomer_program_execution_was_created(sender, instance, created, *args, **kwargs):
    if created:
        #reduce the customer_programs time_account by the program_time_saved_in_seconds
        obj = NadooitCustomerProgram.objects.get(id = instance.customer_program.id)
        obj.time_account.time_balance_in_seconds = obj.time_account.time_balance_in_seconds - instance.program_time_saved_in_seconds
        obj.time_account.save()

