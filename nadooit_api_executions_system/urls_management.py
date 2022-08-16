from django.urls import path

from .views.management import create_token, index_management
#removed , token

urlpatterns = [
    path('create', create_token, name="create-token"),
    path('', index_management, name="manage-token"),
]
