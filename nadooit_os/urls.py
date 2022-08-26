from django.urls import path,include

from nadooit_os.views import index_nadooit_os

urlpatterns = [
    path('', index_nadooit_os, name="nadooit-os"),
]
