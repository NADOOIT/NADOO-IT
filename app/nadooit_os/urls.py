from django.urls import path

from nadooit_os.views import *

app_name = "nadooit_os"

urlpatterns = [
    path("", index_nadooit_os, name="nadooit-os"),
    path(
        "time-account/customer-time-account-overview",
        customer_time_account_overview,
        name="customer-time-account-overview",
    ),
    path(
        "time-account/give-customer-time-account-manager-role",
        give_customer_time_account_manager_role,
        name="give-customer-time-account-manager-role",
    ),
    path(
        "customer-program-execution/customer-order-overview",
        customer_program_execution_overview,
        name="customer-order-overview",
    ),
    path("api_key/create-api-key", create_api_key, name="create-api-key"),
    # Page to revoke API key their API key
    path("api_key/revoke-api-key", revoke_api_key, name="revoke-api-key"),
""" Deactivate API key Manager role    
    path(
        "api_key/give-api-key-manager-role",
        give_api_key_manager_role,
        name="give-api-key-manager-role",
    ),
     """
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
    # These are the urls for the hr department of the company
    # They include an overview of all employees and the possibility to create new employees, edit them and delete them
    # An employee can be selected and their profile can be viewed
    # The employee profile contains the employee's personal information and the employee's roles, which are the rights the employee has, e.g. the right to create customer programs
    # It also contains the option to see the employees contracts and the option to create a new contract for the employee
    path(
        "hr/employee-overview",
        employee_overview,
        name="employee-overview",
    ),
    # This is the url for the profile of an employee
    path(
        "hr/employee-profile/<int:employee_id>",
        employee_profile,
        name="employee-profile",
    ),
    path(
        "hr/add-employee",
        add_employee,
        name="add-employee",
    ),
    path(
        "hr/give-employee-manager-role",
        give_employee_manager_role,
        name="give-employee-manager-role",
    ),
]
