from django.db import models
import uuid

from nadooit_crm.models import Customer

# Create your models here.
class Team(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True, editable=True)
    updated_at = models.DateTimeField(auto_now=True, editable=True)

    def __str__(self):
        return self.name

class Developer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    teams = models.ManyToManyField(Team, related_name='developer_teams')
    created_at = models.DateTimeField(auto_now_add=True, editable=True)
    updated_at = models.DateTimeField(auto_now=True, editable=True)

    def __str__(self):
        return self.name

class Program(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField()
    team_id = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=True)
    updated_at = models.DateTimeField(auto_now=True, editable=True)

    def __str__(self):
        return self.name

class CustomerProgram(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    program_time_saved = models.CharField(max_length=255)
    program_balance = models.CharField(max_length=255)
    over_charge = models.BooleanField(default=False)
    program_id = models.ForeignKey(Program, on_delete=models.SET_NULL, null=True)
    customer_id = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=True)
    updated_at = models.DateTimeField(auto_now=True, editable=True)

    def __str__(self):
        return self.program_id.name


class CustomerProgramExecution(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    program_time_saved = models.CharField(max_length=255)
    customer_program_id = models.ForeignKey(CustomerProgram, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=True)
    updated_at = models.DateTimeField(auto_now=True, editable=True)

    def __str__(self):
        return self.customer_program_id.program_id.name
