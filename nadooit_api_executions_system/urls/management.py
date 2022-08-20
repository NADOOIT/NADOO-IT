from django.urls import path

from nadooit_api_executions_system.views.management import index_management,create_api_key

urlpatterns = [
    path('', index_management, name="manage"),
    path('create-api-key', create_api_key, name="create-api-key"),
]
