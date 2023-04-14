# Author: Christoph Backhaus
# Date: 2022-10-30
# Version: 1.0.0
# Description: This is the urls file for the nadooit app. It contains the urls for the app. From this file the urls are loaded into the main urls.py file.
# Compatibility: Django 4
# License: TBD

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
import mfa
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.urls import include, path

admin.site.site_header = "NADOOIT Administration"  # default: "Django Administration"
admin.site.index_title = "NADOOIT Administration Site"  # default: "Site administration"
admin.site.site_title = "NADOOIT"

# This is where the urls are placed
urlpatterns = [
    # These are the urls for the webpage
    path(
        "",
        include(
            ("nadooit_website.urls", "nadooit_website"), namespace="nadooit_website"
        ),
    ),
    path(
        "",
        include("nadooit_questions_and_answers.urls"),
        name="nadooit_questions_and_answers",
    ),
    # These are the urls for the adminbackend
    path("admin/", admin.site.urls),
    # These are the urls for the django debug toolbar
    path("__debug__/", include("debug_toolbar.urls")),
    # These are the urls for the grappelli skin for the admin page
    path("grappelli/", include("grappelli.urls")),
    # These are the the urls for implementing the pwa for the django app
    path("", include("pwa.urls")),
    # These are the urls for multi factor authentication
    path(
        "mfa/",
        include("mfa.urls"),
        name="mfa",
    ),
    # This short link to add new trusted device
    # path("devices/add", mfa.TrustedDevice.add, name="mfa_add_new_trusted_device"),
    # Routes for the nadooit system
    # These are the urls for everything that has to do with user authentication. Including login, logout and registration
    path("auth/", include("nadooit_auth.urls", namespace="nadooit_auth")),
    # These are the entrypoints for the apis
    # TODO rename route to so that multiple API routes are possible for future APIs
    path("api/", include("nadooit_api_executions_system.urls")),
    # These are the urls for the nadooit_os with is the app for the nadooit system.
    path("nadooit-os/", include("nadooit_os.urls", namespace="nadooit_os")),
    # These are the routes for the ownership system for software in the nadoo network
    # TODO rename to include nadoo naming sceama
    path("program_ownership/", include("nadooit_program_ownership_system.urls")),
]
# + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    # OLD urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
