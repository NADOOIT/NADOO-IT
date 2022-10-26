import hashlib
import uuid
from django.db import models
from nadooit_hr.models import Employee
from nadooit_crm.models import Customer

from nadooit_auth.models import User
from django.dispatch import receiver

# Create your models here.


class NadooitApiKey(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # api_keys are unique and are stored in the database as a hash of the api key
    api_key = models.CharField(
        max_length=255,
        unique=True,
        editable=True,
        null=False,
        blank=False,
        default=uuid.uuid4,
    )
    created_at = models.DateTimeField(auto_now_add=True, editable=True)
    updated_at = models.DateTimeField(auto_now=True, editable=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        if self.user.display_name != "":
            return f"{self.user.display_name}  {self.user.user_code}"
        else:
            return f"{self.user.username}  {self.user.user_code}"


"""         
    def save(self, *args, **kwargs):
        if not self.pk:
            print("this used to work...")
            self.api_key = hashlib.sha256(str(self.api_key).encode()).hexdigest()
        
        super(NadooitApiKey, self).save(*args, **kwargs)
        """


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
    customers_the_manager_is_responsible_for = models.ManyToManyField(
        Customer, blank=True
    )

    def __str__(self):
        if self.employee.user.display_name != "":
            return f"{self.employee.user.display_name}  {self.employee.user.user_code}"
        elif self.employee.user.username != "":
            return f"{self.employee.user.username}  {self.employee.user.user_code}"
        else:
            return f"{self.employee.user.user_code}"
