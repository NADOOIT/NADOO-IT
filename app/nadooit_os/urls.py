from django.urls import path

from nadooit_os.views import index_nadooit_os

app_name = "nadooit_os"

urlpatterns = [
    path("", index_nadooit_os, name="nadooit-os"),
]
