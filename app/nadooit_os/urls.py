from django.urls import path

from nadooit_os.views import *

app_name = "nadooit_os"

urlpatterns = [
    path("", index_nadooit_os, name="nadooit-os"),
    path(
        "customer-time-account-overview",
        customer_time_account_overview,
        name="customer-time-account-overview",
    ),
    path(
        "customer-program-execution/customer-order-overview",
        customer_program_execution_overview,
        name="customer-order-overview",
    ),
    path("create-api-key", create_api_key, name="create-api-key"),
    # Page to revoke API key their API key
    path("revoke-api-key", revoke_api_key, name="revoke-api-key"),
    path(
        "give-api-key-manager-role",
        give_api_key_manager_role,
        name="give-api-key-manager-role",
    ),
    path(
        "give-customer-time-account-manager-role",
        give_customer_time_account_manager_role,
        name="give-customer-time-account-manager-role",
    ),
    path(
        "customer-program-execution/give-customer-program-execution-manager-role",
        give_customer_program_execution_manager_role,
        name="give-customer-program-execution-manager-role",
    ),
    # urls for customer programs and the profile of the customer programs
    path(
        "customer-program/customer-program-overview",
        customer_program_overview,
        name="customer-program-overview",
    ),
    path(
    "customer-program/give-customer-program-manager-role",
    give_customer_program_manager_role,
    name="give-customer-program-manager-role",
    ),
]
