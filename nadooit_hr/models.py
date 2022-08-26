import uuid
from django.db import models
from nadooit_auth.models import User
from nadooit_crm.models import Customer

# Create your models here.
    
class Employee(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    #a customers field that shows what customers the employee is assigned to
    customers = models.ManyToManyField(Customer)
    
    def __str__(self):
        if self.user.display_name != "":
            return self.user.display_name
        else:
            return self.user.username	    
