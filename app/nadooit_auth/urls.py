# Author: Christoph Backhaus
# Date: 2022-10-30
# Version: 1.0.0
# Compatibility: Django 4
# License: TBD

from django.urls import path
from nadooit_auth.views import login_user, logout_user, register_user

app_name = "nadooit_auth"

urlpatterns = [
    # path for login
    path("login-user", login_user, name="login-user"),
    # path for logout
    path("logout-user", logout_user, name="logout-user"),
    # path for registering a new user
    path("register-user", register_user, name="register-user"),
]
