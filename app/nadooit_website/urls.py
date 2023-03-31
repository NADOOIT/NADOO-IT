from django.urls import path

from . import views

# This is where the urls are placed
urlpatterns = [
    path("", views.index, name="index"),
    path("new_index", views.new_index, name="new_index"),
    path("impressum", views.impressum, name="impressum"),
    path("datenschutz", views.datenschutz, name="datenschutz"),
    path("statistics", views.statistics, name="statistics"),
]
