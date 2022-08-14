from django.urls import path

from .views import create_execution, check_user
#removed , token

urlpatterns = [
    path('executions', create_execution, name="create"),
    #path('token', token, name="create_token"),
    path('users/check', check_user, name="check"),
]
