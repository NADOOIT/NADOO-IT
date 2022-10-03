from django.urls import path
from nadooit_auth.views import login_user, logout_user, register_user

app_name = "nadooit_auth"

urlpatterns = [
    path("login-user", login_user, name="login-user"),
    path("logout-user", logout_user, name="logout-user"),
    path("register-user", register_user, name="register-user"),
]
