#Author: Christoph Backhaus
#Date: 2022-10-30
#Version: 1.0.0
#Description: This is the urls file for the nadooit app. It contains the urls for the app. From this file the urls are loaded into the main urls.py file.
#Compatibility: Django 3.2.8
#License: TBD

"""NADOOIT URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf.urls.static import static
from django.urls import path, include

import mfa
import mfa.TrustedDevice

from django.conf import settings

admin.site.site_header = "NADOOIT Administration"  # default: "Django Administration"
admin.site.index_title = "NADOOIT Administration Site"  # default: "Site administration"
admin.site.site_title = "NADOOIT"

# This is where the urls are placed
urlpatterns = [
    path("", include("nadooit_website.urls")),
    path("admin/", admin.site.urls),
    path("auth/", include("nadooit_auth.urls", namespace="nadooit_auth")),
    path("api/", include("nadooit_api_executions_system.urls")),
    path("nadooit-os/", include("nadooit_os.urls", namespace="nadooit_os")),
    path("__debug__/", include("debug_toolbar.urls")),
    path("grappelli/", include("grappelli.urls")),
    path("", include("pwa.urls")),
    path("mfa/", include("mfa.urls")),
    path(
        "devices/add", mfa.TrustedDevice.add, name="mfa_add_new_trusted_device"
    ),  # This short link to add new trusted device
    path("program_ownership/", include("nadooit_program_ownership_system.urls")),
]
# + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    # OLD urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
