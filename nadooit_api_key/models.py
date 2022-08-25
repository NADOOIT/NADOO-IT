import hashlib
import uuid
from django.db import models

from nadooit_auth.models import User

# Create your models here.

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
            print("this used to work...")
            self.api_key = hashlib.sha256(str(self.api_key).encode()).hexdigest()
        
        super(NadooitApiKey, self).save(*args, **kwargs)