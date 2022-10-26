from django.urls import path

from nadooit_os.views import *

app_name = "nadooit_os"

urlpatterns = [
    path("", index_nadooit_os, name="nadooit-os"),
    path(
        "customer_time_account_overview",
        customer_time_account_overview,
        name="customer_time_account_overview",
    ),
    path(
        "orders_overview",
        customer_order_overview,
        name="customer_order_overview",
    ),
    path("create-api-key", create_api_key, name="create-api-key"),
    # Page to revoke API key their API key
    path("revoke-api-key", revoke_api_key, name="revoke-api-key"),
]
