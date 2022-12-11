# Author: Christoph Backhaus
# Date: 2022-10-30
# Version: 1.0.0
# Compatibility: Django 4
# License: TBD

from django.contrib.auth.backends import BaseBackend


class UserCodeBackend(BaseBackend):
    def authenticate(self, request, user_code=None):
        from nadooit_auth.models import User

        try:
            user = User.objects.get(user_code=user_code)
            return user
        except User.DoesNotExist:
            return None

    def get_user(self, user_code):
        from nadooit_auth.models import User

        try:
            return User.objects.get(user_code=user_code)
        except User.DoesNotExist:
            return None
