import hashlib
import uuid
from django.db import models
from nadooit_hr.models import Employee
from nadooit_crm.models import Customer

from nadooit_auth.models import User
from django.dispatch import receiver

# Create your models here.

# Model for a Nadooit API Key. This is used to authenticate the user when he makes a request to the API.
# Each user has a unique API Key.
class NadooitApiKey(models.Model):
    # id of the api key
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # the user that owns the api key
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # api_keys are unique and are stored in the database as a hash of the api key
    # this is done to prevent the api key from being stored in plain text in the database
    api_key = models.CharField(
        max_length=255,
        unique=True,
        editable=True,
        null=False,
        blank=False,
        default=uuid.uuid4,
    )
    
    # date and time when the api key was created
    created_at = models.DateTimeField(auto_now_add=True, editable=True)
    updated_at = models.DateTimeField(auto_now=True, editable=True)
    
    # property that tracs if the api key still active or not
    is_active = models.BooleanField(default=True)

    def __str__(self):
        if self.user.display_name != "":
            return f"{self.user.display_name}  {self.user.user_code}"
        else:
            return f"{self.user.username}  {self.user.user_code}"

# function that is called when a new api key is created
@receiver(models.signals.post_save, sender=NadooitApiKey)
def hash_api_key_when_created(sender, instance, created, *args, **kwargs):
    if created:
        # hashes the api_key
        obj = NadooitApiKey.objects.get(id=instance.id)
        obj.api_key = hashlib.sha256(str(obj.api_key).encode()).hexdigest()
        obj.save()


# A role class that gets added to the user model
# It is used to determine what the user can do in regards to the Nadooit Api Key
class NadooitApiKeyManager(models.Model):
    employee = models.OneToOneField(
        Employee, on_delete=models.CASCADE, primary_key=True
    )

    can_create_api_key = models.BooleanField(default=False)
    can_delete_api_key = models.BooleanField(default=False)
    
    can_give_ApiKeyManager_role = models.BooleanField(default=False)
    
    list_of_customers_the_manager_is_responsible_for = models.ManyToManyField(
        Customer, blank=True
    )
    
    list_of_employees_the_manager_has_given_the_role_to = models.ManyToManyField(
        Employee, blank=True, related_name="list_of_employees_the_api_key_manager_has_given_the_role_to"
    )

    def __str__(self):
        if self.employee.user.display_name != "":
            return f"{self.employee.user.display_name}  {self.employee.user.user_code}"
        elif self.employee.user.username != "":
            return f"{self.employee.user.username}  {self.employee.user.user_code}"
        else:
            return f"{self.employee.user.user_code}"
