from django.db import models
import uuid

# Create your models here.
from django.db.models import ForeignKey


class Token(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_code = models.CharField(max_length=255)
    token = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=True)
    updated_at = models.DateTimeField(auto_now=True, editable=True)

    def __str__(self):
        return self.user_code


class Team(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True, editable=True)
    updated_at = models.DateTimeField(auto_now=True, editable=True)

    def __str__(self):
        return self.name


class Address(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    street = models.CharField(max_length=255, null=True, blank=True)
    house_number = models.CharField(max_length=255, null=True, blank=True)
    town = models.CharField(max_length=255, null=True, blank=True)
    postal_code = models.CharField(max_length=255, null=True, blank=True)
    addressed_to = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=True)
    updated_at = models.DateTimeField(auto_now=True, editable=True)

    def __str__(self):
        return self.postal_code


class Developer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    teams = models.ManyToManyField(Team, related_name='developer_teams')
    created_at = models.DateTimeField(auto_now_add=True, editable=True)
    updated_at = models.DateTimeField(auto_now=True, editable=True)

    def __str__(self):
        return self.name


class Customer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    addresses = models.ManyToManyField(Address, related_name='customer_addresses')
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
