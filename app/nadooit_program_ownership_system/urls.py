from django.urls import path

from . import views

# This is where the urls are placed
urlpatterns = [
    path("admin", views.admin, name="customer_program_ownership_overview_adminpage"),
    path(
        "customer_program_ownership_overview",
        views.customer_program_ownership_overview,
        name="customer_program_ownership_overview",
    ),
]
