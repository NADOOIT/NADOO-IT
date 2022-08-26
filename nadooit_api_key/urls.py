from django.urls import path,include

from nadooit_api_key.views import api_key_interface, create_api_key



urlpatterns = [
    path('', api_key_interface, name="api-key-interface"),	
    path('create-api-key', create_api_key, name="create-api-key"),
]
