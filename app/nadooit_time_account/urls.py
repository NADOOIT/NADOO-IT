from django.urls import path
from . import views

# This is where the urls are placed
urlpatterns = [
    path("admin", views.admin, name="adminpage"),
    path(
        "customer_time_account_overview",
        views.customer_time_account_overview,
        name="customer_time_account_overview",
    ),
    path(
        "orders_overview",
        views.customer_order_overview,
        name="customer_order_overview",
    ),
]
