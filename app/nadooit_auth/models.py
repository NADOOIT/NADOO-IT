# Author: Christoph Backhaus
# Date: 2022-10-30
# Version: 1.0.0
# Compatibility: Django 4
# License: TBD

import uuid

from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.db import models
from nadooit_auth.user_code import get__new_user_code

# Create your models here.

# User model that extends the default Django user model. It has two additional fields:
# - user_code: a unique code that is used to identify the user
# - display_name: the name that is displayed in the UI
class User(AbstractUser, PermissionsMixin):

    # id is a unique identifier for the user
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # The user code is a unique code that is used to identify the user.
    # The user code is generated automatically when the user is created.
    # The user can change the user code in the settings.
    # The user code is wirrten on the user's security key.
    # TODO: #114 rename to code because it is already in the user model
    user_code = models.CharField(
        max_length=32,
        unique=True,
        editable=True,
        null=False,
        blank=False,
        default=get__new_user_code,
    )

    # The display name is the name that is displayed in the UI.
    display_name = models.CharField(max_length=32, editable=True)

    def __str__(self):
        if self.display_name != "":
            return self.display_name
        else:
            return self.username
