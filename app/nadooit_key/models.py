from django.db import models
from nadooit_hr.models import Employee

# The KeyManager extends the User model
# Managing keys means that the KeyManager can have some of the following abillitys create, delete and update keys for other users
# The KeyManager can also can also give other users the ability it has and make them into KeyManagers themselves
# The KeyManager is represented is if the display_name is exisiting, otherwise the user_code is used
class KeyManager(models.Model):
    
    user = models.OneToOneField(Employee, on_delete=models.CASCADE)
    
    
    can_create_keys = models.BooleanField(default=False)
    can_delete_keys = models.BooleanField(default=False)
    can_update_keys = models.BooleanField(default=False)
    
    
    can_create_key_managers = models.BooleanField(default=False)
    can_delete_key_managers = models.BooleanField(default=False)
    can_update_key_managers = models.BooleanField(default=False)
    
    key_managers_assigened_by_this_key_manager = models.ManyToManyField("self", blank=True)

    def __str__(self):
        if self.user.user.display_name != "":
            return self.user.user.display_name
        else:
            return self.user.user.user_code
