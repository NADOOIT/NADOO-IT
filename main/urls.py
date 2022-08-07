from django.urls import path

from .views import create_execution, token, check_user

urlpatterns = [
    path('', create_execution, name="create"),
    path('token', token, name="create_token"),
    path('check', check_user, name="check"),
]
