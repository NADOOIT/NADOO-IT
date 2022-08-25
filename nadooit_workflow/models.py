import uuid
from django.db import models

from nadooit_program_ownership_system.models import NadooitProgram
from nadooit_crm.models import Customer

# Create your models here.
class Process(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    #process_trigger_evnets is a list of events that trigger the process. They are represented as a list of strings.
    #process_trigger_events = models.CharField(max_length=255)	#list of events that trigger the process.
    #process_subscriptions = models.CharField(max_length=255)
    trigger_process = models.ForeignKey('self', on_delete=models.SET_NULL, null=True)
    tiggers_process = models.ManyToManyField('self', blank=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True, editable=True)
    updated_at = models.DateTimeField(auto_now=True, editable=True)
    list_of_nadooit_programs = models.ManyToManyField(NadooitProgram)

    def __str__(self):
        return self.name	