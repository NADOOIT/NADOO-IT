from django.urls import path

from .views import create_execution, token, check_user

urlpatterns = [
    path('executions', create_execution, name="create"),
    #path('token', token, name="create_token"),
    path('users/check', check_user, name="check"),
]
