from django.urls import path

from nadooit_api_executions_system.views.management import create_token, index_management

urlpatterns = [
    path('create', create_token, name="create-token"),
    path('', index_management, name="manage-token"),
]
