import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser, PermissionsMixin


from nadooit_auth.user_code import get__new_user_code

# Create your models here.
class User(AbstractUser,PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_code = models.CharField(max_length=32, unique=True, editable=True, null=False, blank=False,default=get__new_user_code)
    display_name = models.CharField(max_length=32, editable=True)
    
    def __str__(self):
        if self.display_name != "":
            return self.display_name
        else:
            return self.username
    #Every User can have multiple api_keys
    #objects = CustomUserManager()
