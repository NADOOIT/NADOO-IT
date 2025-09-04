from django.urls import path
from django.contrib.auth.decorators import login_required
from nadooit_os.views import *

app_name = "nadooit_os"

urlpatterns = [
    path("", login_required(index_nadooit_os), name="nadooit-os"),
    path(
        "time-account/customer-time-account-overview",
        login_required(customer_time_account_overview),
        name="customer-time-account-overview",
    ),
    path(
        "time-account/give-customer-time-account-manager-role",
        login_required(give_customer_time_account_manager_role),
        name="give-customer-time-account-manager-role",
    ),
    path(
        "customer-program-execution/customer-order-overview",
        login_required(customer_program_execution_overview),
        name="customer-order-overview",
    ),
    path(
        "customer-program-execution-filter-tabs/<filter_type>/<uuid:cutomer_id>",
        login_required(customer_program_execution_list_for_cutomer),
        name="customer-program-execution-filter-tabs",
    ),
    path(
        "customer-program-execution-list-for-cutomer/<filter_type>/<uuid:cutomer_id>",
        login_required(customer_program_execution_list_for_cutomer),
        name="customer-program-execution-list-for-cutomer",
    ),
    path(
        "customer-program-execution/export/<filter_type>/<uuid:cutomer_id>",
        login_required(export_transactions),
        name="export-transactions",
    ),
    path(
        "customer-program-execution-list-complaint-modal/<uuid:customer_program_execution_id>",
        login_required(customer_program_execution_list_complaint_modal),
        name="customer-program-execution-list-complaint-modal",
    ),
    path(
        "customer-program-execution-send-complaint/<uuid:customer_program_execution_id>",
        login_required(customer_program_execution_send_complaint),
        name="customer-program-execution-send-complaint",
    ),
    path("api_key/create-api-key", login_required(create_api_key), name="create-api-key"),
    # Page to revoke API key their API key
    path("api_key/revoke-api-key", login_required(revoke_api_key), name="revoke-api-key"),
    path(
        "customer-program-execution/give-customer-program-execution-manager-role",
        login_required(give_customer_program_execution_manager_role),
        name="give-customer-program-execution-manager-role",
    ),
    # urls for customer programs and the profile of the customer programs
    path(
        "customer-program/customer-program-overview",
        login_required(customer_program_overview),
        name="customer-program-overview",
    ),
    path(
        "customer-program/customer-program-profile/<uuid:customer_program_id>",
        login_required(get__customer_program_profile),
        name="customer-program-profile",
    ),
    path(
        "customer-program/give-customer-program-manager-role",
        login_required(give_customer_program_manager_role),
        name="give-customer-program-manager-role",
    ),
    # These are the urls for the hr department of the company
    # They include an overview of all employees and the possibility to create new employees, edit them and delete them
    # An employee can be selected and their profile can be viewed
    # The employee profile contains the employee's personal information and the employee's roles, which are the rights the employee has, e.g. the right to create customer programs
    # It also contains the option to see the employees contracts and the option to create a new contract for the employee
    path(
        "hr/employee-overview",
        login_required(employee_overview),
        name="employee-overview",
    ),
    # This is the url for the profile of an employee
    # TODO: This url is not done yet
    # path(
    #    "hr/employee-profile/<employee_id>",
    #    employee_profile,
    #    name="employee-profile",
    # ),
    path(
        "hr/my-profile",
        login_required(employee_profile),
        name="my-profile",
    ),
    path(
        "hr/add-employee",
        login_required(add_employee),
        name="add-employee",
    ),
    path(
        "hr/give-employee-manager-role",
        login_required(give_employee_manager_role),
        name="give-employee-manager-role",
    ),
    path(
        "hr/deactivate-contract/<employee_contract_id>",
        login_required(deactivate_contract),
        name="deactivate-contract",
    ),
    path(
        "hr/activate-contract/<employee_contract_id>",
        login_required(activate_contract),
        name="activate-contract",
    ),
]
