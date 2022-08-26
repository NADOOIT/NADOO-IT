from django.urls import path

from nadooit_api_executions_system.views import create_execution, check_user

urlpatterns = [
    path('executions', create_execution, name="create"),
    path('users/check', check_user, name="check"),
]
