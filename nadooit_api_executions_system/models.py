import hashlib
from django.db import models
import uuid
from django.contrib.auth.models import AbstractUser, PermissionsMixin

from nadooit_api_executions_system.user_code import get__new_user_code

# Create your models here.

class User(AbstractUser,PermissionsMixin):
    user_code = models.CharField(max_length=32, unique=True, editable=True, null=False, blank=False,default=get__new_user_code)
    display_name = models.CharField(max_length=32, editable=True)
    
    def __str__(self):
        if self.display_name != "":
            return self.display_name
        else:
            return self.username
    #Every User can have multiple api_keys
    #objects = CustomUserManager()


class NadooitApiKey(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    #api_keys are unique and are stored in the database as a hash of the api key
    api_key = models.CharField(max_length=255, unique=True, editable=True, null=False, blank=False,default=uuid.uuid4)
    created_at = models.DateTimeField(auto_now_add=True, editable=True)
    updated_at = models.DateTimeField(auto_now=True, editable=True)
    is_active = models.BooleanField(default=True) 
    
    def __str__(self):
        if self.user.display_name != "":
            return f'{self.user.display_name}  {self.user.user_code}'
        else:
            return f'{self.user.username}  {self.user.user_code}'
        
    def save(self, *args, **kwargs):
        if not self.pk:
            self.api_key = hashlib.sha256(str(self.api_key).encode()).hexdigest()
        super(NadooitApiKey, self).save(*args, **kwargs)
    
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
        return self.street + ' ' + self.house_number + ' ' + self.town + ' ' + self.postal_code + ' ' + self.addressed_to	


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
