from django.urls import path,include
from nadooit_auth.views import login_user, logout_user

urlpatterns = [
    path('login-user', login_user, name="login-user"),
    path('logout-user', logout_user, name="logout-user"),
]
