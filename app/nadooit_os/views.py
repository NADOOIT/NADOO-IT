import csv
from uuid import uuid4

from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import (
    HttpRequest,
    HttpResponse,
    HttpResponseForbidden,
    HttpResponseNotFound,
    HttpResponseRedirect,
)
from django.shortcuts import render
from nadooit_hr.models import EmployeeContract

import logging

logger = logging.getLogger(__name__)


from django.views.decorators.http import require_GET, require_POST
from nadooit_api_executions_system.models import CustomerProgramExecution
from nadooit_auth.models import User

# Manager Roles
from nadooit_hr.models import (
    CustomerProgramExecutionManagerContract,
    CustomerProgramManagerContract,
    Employee,
    EmployeeContract,
    EmployeeManagerContract,
    TimeAccountManagerContract,
)
from nadooit_os.services import (
    check__active_customer_program_execution_manager_contract__exists__between__employee_and_customer,
    check__customer__exists__for__customer_id,
    check__customer_program__for__customer_program_id__exists,
    check__customer_program_execution__exists__for__customer_program_execution_id,
    check__employee_manager_contract__exists__for__employee_manager_and_customer__and__can_add_users__and__is_active,
    check__employee_manager_contract__for__user__can_deactivate__employee_contracts,
    check__employee_manager_contract__for__user__can_give_manager_role,
    check__more_then_one_contract_between__user_code__and__customer,
    check__user__exists__for__user_code,
    check__user__is__customer_program_manager__for__customer_prgram,
    create__customer_program_execution_complaint__for__customer_program_execution_and_complaint_and_employee,
    create__customer_program_execution_manager_contract__for__employee_and_customer_and_list_of_abilities_and_employee_with_customer_program_manager_contract,
    create__customer_program_execution_manager_contract__for__employee_contract,
    create__employee_manager_contract__for__user_code_customer_and_list_of_abilities_according_to_employee_creating_contract,
    create__NadooitApiKey__for__user,
    create__time_account_manager_contract__for__user_code_customer_and_list_of_abilities_according_to_employee_creating_contract,
    get__active_employee_contract__for__employee__and__customer,
    get__csv__for__list_of_customer_program_executions,
    get__customer__for__customer_id,
    get__customer__for__customer_program_execution_id,
    get__customer_program__for__customer_program_id,
    get__customer_program_execution__for__customer_program_execution_id,
    get__customer_program_executions__for__filter_type_and_customer,
    get__customer_program_manager_contract__for__employee_and_customer,
    get__customer_time_accounts_grouped_by_customer_with_total_time_of_all_time_accounts__for__employee,
    get__employee__for__employee_id,
    get__employee__for__user_code,
    get__employee_contract__for__employee__and__customer,
    get__employee_contract__for__employee_contract_id,
    get__employee_contract__for__user_code__and__customer,
    get__employee_manager_contract__for__user_code__and__customer,
    get__list_of_abilities__for__list_of_selected_abilities_and_list_of_possible_abilities_the_employee_can_give,
    get__list_of_abilties__for__customer_program_manager_contract,
    get__list_of_customer_program_execution__for__employee_and_filter_type__grouped_by_customer,
    get__list_of_customer_program_execution_manager_contract__for__employee,
    get__list_of_customers__and__their_employees__for__customers_that_have_a_employee_manager_contract__for__user,
    get__list_of_customers__for__employee_manager_contract__that_can_add_employees__for__user,
    get__list_of_customers__for__employee_manager_contract__that_can_give_the_role__for__user,
    get__list_of_customers__for__employee_that_has_a_time_account_manager_contract_with_and_can_create_time_account_manager_contracts_for_them,
    get__list_of_customers_the_employee_has_a_customer_program_execution_manager_contract_with_and_can_create_such_a_contract,
    get__list_of_customers_the_employee_has_a_customer_program_manager_contract_with_and_can_create_such_a_contract,
    get__list_of_customers_the_employee_has_a_customer_programm_manager_contract_with_and_the_customer_programms__for__employee,
    get__list_of_manager_contracts__for__employee,
    get__next_price_level__for__customer_program,
    get__not_paid_customer_program_executions__for__filter_type_and_customer,
    get__price_as_string_in_euro_format__for__price_in_euro_as_decimal,
    get__sum_of_price_for_execution__for__list_of_customer_program_exections,
    get__sum_of_time_saved_in_seconds__for__list_of_customer_program_exections,
    get__time_as_string_in_hour_format__for__time_in_seconds_as_integer,
    get__user_info__for__user,
    set__all_active_NadooitApiKey__for__user_to_inactive,
    set__employee_contract__is_active_state__for__employee_contract_id,
    set__list_of_abilities__for__customer_program_manager_contract_according_to_list_of_abilities,
    set__payment_status__for__customer_program_execution,
    set_employee_contract__as_inactive__for__employee_contract_id,
)

from nadooit_hr.models import EmployeeManagerContract
from .forms import ApiKeyForm

# imoport for userforms


# Tests for user roles

# Tests for Time Account Manager
def user_is_Time_Account_Manager(user: User) -> bool:
    if TimeAccountManagerContract.objects.filter(
        contract__employee=user.employee,
        contract__is_active=True,
    ).exists():
        return True
    else:
        return False


def user_is_Time_Account_Manager_and_can_give_manager_role(
    user: User,
) -> bool:
    if TimeAccountManagerContract.objects.filter(
        contract__employee=user.employee,
        contract__is_active=True,
        can_give_manager_role=True,
    ).exists():
        return True
    else:
        return False


# Tests for Api Key Manager
def user_is_Api_Key_Manager(user: User) -> bool:
    if hasattr(user.employee, "nadooitapikeymanager"):
        return True
    return False


def user_is_Api_Key_Manager_and_can_give_manager_role(user: User) -> bool:
    if hasattr(user.employee, "nadooitapikeymanager"):
        if user.employee.nadooitapikeymanager.can_give_manager_role:
            return True
    return False


# Tests for Customer Program Execution Manager
def user_is_Customer_Program_Execution_Manager(user: User) -> bool:
    # checks if the employee for the user is an employee manager
    if CustomerProgramExecutionManagerContract.objects.filter(
        contract__employee=user.employee, contract__is_active=True
    ).exists():
        return True
    else:
        return False


def user_is_Customer_Program_Execution_Manager_and_can_give_Customer_Program_Execution_Manager_role(
    user: User,
) -> bool:
    if CustomerProgramExecutionManagerContract.objects.filter(
        contract__employee=user.employee,
        contract__is_active=True,
        can_give_manager_role=True,
    ).exists():
        return True
    else:
        return False


# Tests for Customer Program Manager
def user_is_Customer_Program_Manager(user: User) -> bool:
    # checks if the employee for the user is an employee manager
    if CustomerProgramManagerContract.objects.filter(
        contract__employee=user.employee, contract__is_active=True
    ).exists():
        return True
    else:
        return False


def user_is_Customer_Program_Manager_and_can_give_Customer_Program_Manager_role(
    user: User,
) -> bool:
    if CustomerProgramManagerContract.objects.filter(
        contract__employee=user.employee,
        contract__is_active=True,
        can_give_manager_role=True,
    ).exists():
        return True
    else:
        return False


# Tests for Employee Manager
def user_is_Employee_Manager(user: User) -> bool:
    # checks if the employee for the user is an employee manager
    if EmployeeManagerContract.objects.filter(
        contract__employee=user.employee, contract__is_active=True
    ).exists():
        return True
    else:
        return False


def user_is_Employee_Manager_and_can_give_Employee_Manager_role(
    user: User,
) -> bool:
    if check__employee_manager_contract__for__user__can_give_manager_role(user):
        return True
    else:
        return False


def user_is_Employee_Manager_and_can_add_new_employee(
    user: User,
) -> bool:
    if EmployeeManagerContract.objects.filter(
        contract__employee=user.employee,
        contract__is_active=True,
        can_add_new_employee=True,
    ).exists():
        return True
    else:
        return False


def user_is_Employee_Manager_and_can_delete_employee(
    user: User,
) -> bool:
    if check__employee_manager_contract__for__user__can_deactivate__employee_contracts(
        user
    ):
        return True
    else:
        return False


# Getting the user roles
# If new roles are added, they need to be added here
# this function uses the user_is_... functions above
def get__employee_roles_and_rights__for__employee(employee: Employee) -> dict:
    return {
        "is_time_account_manager": user_is_Time_Account_Manager(employee.user),
        "user_is_Time_Account_Manager_and_can_give_manager_role": user_is_Time_Account_Manager_and_can_give_manager_role(
            employee.user
        ),
        "is_api_key_manager": user_is_Api_Key_Manager(employee.user),
        "user_is_api_key_manager_and_can_give_manager_role": user_is_Api_Key_Manager_and_can_give_manager_role(
            employee.user
        ),
        "is_employee_manager": user_is_Employee_Manager(employee.user),
        "user_is_Employee_Manager_and_can_give_Employee_Manager_role": user_is_Employee_Manager_and_can_give_Employee_Manager_role(
            employee.user
        ),
        "user_is_Employee_Manager_and_can_add_new_employee": user_is_Employee_Manager_and_can_add_new_employee(
            employee.user
        ),
        "is_customer_program_manager": user_is_Customer_Program_Manager(employee.user),
        "user_is_Customer_Program_Manager_and_can_give_Customer_Program_Manager_role": user_is_Customer_Program_Manager_and_can_give_Customer_Program_Manager_role(
            employee.user
        ),
        "is_customer_program_execution_manager": user_is_Customer_Program_Execution_Manager(
            employee.user
        ),
        "user_is_Customer_Program_Execution_Manager_and_can_give_Customer_Program_Execution_Manager_role": user_is_Customer_Program_Execution_Manager_and_can_give_Customer_Program_Execution_Manager_role(
            employee.user
        ),
    }


def get__user__roles_and_rights__for__http_request(request: HttpRequest):
    return get__employee_roles_and_rights__for__employee(request.user.employee)


# Create your views here.
# Main page of the nadooit_os
@login_required(login_url="/auth/login-user")
def index_nadooit_os(request: HttpRequest):

    logger.info("nadoo os accessed")

    return render(
        request,
        "nadooit_os/index.html",
        # context as dict
        # first item is page_title
        # dict from get__user__roles_and_rights__for__http_request is added
        {
            "page_title": "Nadooit OS",
            **get__user__roles_and_rights__for__http_request(request),
        },
    )


# Views for the time account system
@login_required(login_url="/auth/login-user")
@user_passes_test(user_is_Time_Account_Manager, login_url="/auth/login-user")
def customer_time_account_overview(request: HttpRequest):

    # group the customer time accounts by customer and sum up the time balances
    # the dictionary will look like this:
    """
    {
        customer1: {
            customer_time_accounts: [customer_time_account1, customer_time_account2],
            customer_time_account_total_time_balance: 123456
        },
        customer2: {
            customer_time_accounts: [customer_time_account3, customer_time_account4],
            customer_time_account_total_time_balance: 123456
        }
    }
    """
    customer_time_accounts_grouped_by_customer_with_total_time_of_all_time_accounts = {}

    customer_time_accounts_grouped_by_customer_with_total_time_of_all_time_accounts = get__customer_time_accounts_grouped_by_customer_with_total_time_of_all_time_accounts__for__employee(
        request.user.employee
    )

    return render(
        request,
        "nadooit_os/time_account/customer_time_account_overview.html",
        {
            "page_title": "Übersicht der Zeitkonten",
            "customer_time_accounts_grouped_by_customer_with_total_time_of_all_time_accounts": customer_time_accounts_grouped_by_customer_with_total_time_of_all_time_accounts,
            **get__user__roles_and_rights__for__http_request(request),
        },
    )


# API KEYS Views
@login_required(login_url="/auth/login-user")
@user_passes_test(user_is_Api_Key_Manager, login_url="/auth/login-user")
def create_api_key(request: HttpRequest):
    submitted = False
    if request.method == "POST":
        form = ApiKeyForm(request.POST)
        if form.is_valid():

            create__NadooitApiKey__for__user(request.user, form.cleaned_data["api_key"])

            return HttpResponseRedirect(
                "/nadooit-os/api_key/create-api-key?submitted=True"
            )
    else:
        form = ApiKeyForm()
        if "submitted" in request.GET:
            submitted = True

    form = ApiKeyForm
    return render(
        request,
        "nadooit_os/api_key/create_api_key.html",
        {
            "form": form,
            "submitted": submitted,
            "page_title": "NADOOIT API KEY erstellen",
            **get__user__roles_and_rights__for__http_request(request),
        },
    )


@login_required(login_url="/auth/login-user")
def revoke_api_key(request: HttpRequest):

    submitted = False
    if request.method == "POST":
        # get list of all api keys that are active for the user and set them to inactive

        set__all_active_NadooitApiKey__for__user_to_inactive(request.user)

        return HttpResponseRedirect("/nadooit-os/api_key/revoke-api-key?submitted=True")
    else:
        if "submitted" in request.GET:
            submitted = True

    return render(
        request,
        "nadooit_os/api_key/revoke_api_key.html",
        {
            "submitted": submitted,
            "page_title": "NADOOIT API KEY löschen",
            **get__user__roles_and_rights__for__http_request(request),
        },
    )


# This has been deprecated and is not used anymore
""" 
@login_required(login_url="/auth/login-user")
@user_passes_test(
    user_is_Api_Key_Manager_and_can_give_manager_role,
    login_url="/auth/login-user",
)
def give_api_key_manager_role(request: HttpRequest):
    submitted = False
    if request.method == "POST":
        form = ApiKeyManagerForm(
            request.POST,
        )

        if form.is_valid():

            user_code = form.cleaned_data["user_code"]
            # get the employee object for the user
            employee = Employee.objects.get(user__user_code=user_code)

            customers_the_new_manager_is_responsible_for = request.POST.getlist(
                "customers"
            )
            can_create_api_key = form.cleaned_data["can_create_api_key"]
            can_delete_api_key = form.cleaned_data["can_delete_api_key"]
            can_give_manager_role = form.cleaned_data["can_give_manager_role"]

            # check if the user is already an NadooitApiKeyManager
            if user_is_Api_Key_Manager(employee.user):
                # if the employee is already an ApiKeyManager, update the existing ApiKeyManager object but only give more rights
                api_key_manager = NadooitApiKeyManager.objects.get(employee=employee)
                if can_create_api_key == True:
                    api_key_manager.can_create_api_key = True

                if can_delete_api_key == True:
                    api_key_manager.can_delete_api_key = True

                if can_give_manager_role == True:
                    api_key_manager.can_give_manager_role = True

                api_key_manager.save()

            else:

                # create new api key manager
                new_api_key_manager = NadooitApiKeyManager.objects.create(
                    employee=employee,
                    can_create_api_key=can_create_api_key,
                    can_delete_api_key=can_delete_api_key,
                    can_give_manager_role=can_give_manager_role,
                )

                # add the customers the new manager is responsible for
                for customer in customers_the_new_manager_is_responsible_for:
                    new_api_key_manager.list_of_customers_the_manager_is_responsible_for.add(
                        customer
                    )
                new_api_key_manager.save()

            return HttpResponseRedirect(
                "/nadooit-os/give-api-key-manager-role?submitted=True"
            )

    else:
        form = ApiKeyManagerForm(
            request.POST,
        )
        if "submitted" in request.GET:
            submitted = True

    form = ApiKeyManagerForm(
        request.POST,
    )

    list_of_customers_the_manager_is_responsible_for = (
        request.user.employee.nadooitapikeymanager.list_of_customers_the_manager_is_responsible_for.all()
    )

    return render(
        request,
        "nadooit_os/api_key/give_api_key_manager_role.html",
        {
            "page_title": "API Key Manager Rolle vergeben",
            "form": form,
            "submitted": submitted,
            "list_of_customers_the_manager_is_responsible_for": list_of_customers_the_manager_is_responsible_for,
            **get__user__roles_and_rights__for__http_request(request),
        },
    )
"""


@login_required(login_url="/auth/login-user")
@user_passes_test(
    user_is_Time_Account_Manager_and_can_give_manager_role,
    login_url="/auth/login-user",
)
def give_customer_time_account_manager_role(request: HttpRequest):
    submitted = False
    if request.method == "POST":

        user_code = request.POST.get("user_code")

        # check if customer exists
        if not check__customer__exists__for__customer_id(request.POST.get("customers")):
            return HttpResponseRedirect(
                "/nadooit-os/time-account/give-customer-time-account-manager-role?submitted=True&error=Kein gültiger Kunde eingegeben"
            )

        if not check__user__exists__for__user_code(user_code):
            return HttpResponseRedirect(
                "/nadooit-os/time-account/give-customer-time-account-manager-role?submitted=True&error=Kein gültiger Benutzercode eingegeben"
            )

        customer = get__customer__for__customer_id(request.POST.get("customers"))
        list_of_abilities = request.POST.getlist("role")
        employee_creating_contract = request.user.employee

        if (
            create__time_account_manager_contract__for__user_code_customer_and_list_of_abilities_according_to_employee_creating_contract(
                user_code, customer, list_of_abilities, employee_creating_contract
            )
            is not None
        ):
            return HttpResponseRedirect(
                "/nadooit-os/time-account/give-customer-time-account-manager-role?submitted=True"
            )

    else:
        if "submitted" in request.GET:
            submitted = True

    list_of_customers__for__employee_that_has_a_time_account_manager_contract_with_and_can_create_time_account_manager_contracts_for = get__list_of_customers__for__employee_that_has_a_time_account_manager_contract_with_and_can_create_time_account_manager_contracts_for_them(
        request.user.employee
    )

    return render(
        request,
        "nadooit_os/time_account/give_customer_time_account_manager_role.html",
        {
            "page_title": "Zeitkonten Manager Rolle vergeben",
            "submitted": submitted,
            "error": request.GET.get("error"),
            "list_of_customers_the_manager_is_responsible_for": list_of_customers__for__employee_that_has_a_time_account_manager_contract_with_and_can_create_time_account_manager_contracts_for,
            **get__user__roles_and_rights__for__http_request(request),
        },
    )


# Views for the customer program execution overview
@login_required(login_url="/auth/login-user")
@user_passes_test(
    user_is_Customer_Program_Execution_Manager, login_url="/auth/login-user"
)
def customer_program_execution_overview(request: HttpRequest):

    # All orders for the current customer
    # orders are the executions of customerprograms

    # the list of customers that the time accounts that the employee is responsible for belong to
    # the list has for its first element the customer that the employee is responsible for
    # the list has for its second element the ccustomer programm execution for the customer that the employee is responsible for
    list_of_customer_program_execution__for__employee_and_filter_type__grouped_by_customer = (
        []
    )

    filter_type = "last20"

    list_of_customer_program_execution__for__employee_and_filter_type__grouped_by_customer = get__list_of_customer_program_execution__for__employee_and_filter_type__grouped_by_customer(
        request.user.employee, filter_type=filter_type
    )

    return render(
        request,
        "nadooit_os/customer_program_execution/customer_program_execution_overview.html",
        {
            "page_title": "Übersicht der Buchungen",
            "filter_type": filter_type,
            "customers_the_user_is_responsible_for_and_the_customer_programm_executions": list_of_customer_program_execution__for__employee_and_filter_type__grouped_by_customer,
            **get__user__roles_and_rights__for__http_request(request),
        },
    )


@login_required(login_url="/auth/login-user")
@user_passes_test(
    user_is_Customer_Program_Execution_Manager, login_url="/auth/login-user"
)
def customer_program_execution_list_for_cutomer(
    request: HttpRequest, filter_type, cutomer_id
):
    # covered by test
    if not check__customer__exists__for__customer_id(cutomer_id):
        return HttpResponseForbidden()

    # Get the customer
    # covered by test
    customer = get__customer__for__customer_id(cutomer_id)

    # Check if the user is a customer program execution manager for the customer
    if (
        # covered by test
        check__active_customer_program_execution_manager_contract__exists__between__employee_and_customer(
            employee=request.user.employee, customer=customer
        )
        is False
    ):
        return HttpResponseForbidden()

    # Get the executions depending on the filter type
    customer_program_executions = (
        # covered by test
        get__customer_program_executions__for__filter_type_and_customer(
            filter_type, cutomer_id
        )
    )

    if filter_type == "last20":
        customer_program_executions = customer_program_executions[:20]

    total_time_saved_in_seconds = (
        # covered by test
        get__sum_of_time_saved_in_seconds__for__list_of_customer_program_exections(
            customer_program_executions
        )
    )
    total_price_for_execution_decimal = (
        # covered by test
        get__sum_of_price_for_execution__for__list_of_customer_program_exections(
            customer_program_executions
        )
    )
    total_time_saved = (
        # covered by test
        get__time_as_string_in_hour_format__for__time_in_seconds_as_integer(
            total_time_saved_in_seconds
        )
    )
    # print("total_price_for_execution_decimal", total_price_for_execution_decimal)
    total_price_for_execution = (
        # covered by test
        get__price_as_string_in_euro_format__for__price_in_euro_as_decimal(
            total_price_for_execution_decimal
        )
    )

    return render(
        request,
        "nadooit_os/customer_program_execution/components/cutomer_orders_with_tabs.html",
        {
            "filter_type": filter_type,
            "cutomer_id": cutomer_id,
            "cutomer_name": customer.name,
            "customer_program_executions": customer_program_executions,
            "total_time_saved": total_time_saved,
            "total_price_for_execution": total_price_for_execution,
        },
    )


@login_required(login_url="/auth/login-user")
@user_passes_test(
    user_is_Customer_Program_Execution_Manager, login_url="/auth/login-user"
)
def customer_program_execution_list_complaint_modal(
    request: HttpRequest, customer_program_execution_id
):

    # check if the customer program execution exists
    # covered by test
    if not check__customer_program_execution__exists__for__customer_program_execution_id(
        customer_program_execution_id
    ):
        return HttpResponseForbidden()

    # Get the customer
    # covered by test
    customer = get__customer__for__customer_program_execution_id(
        customer_program_execution_id
    )

    if customer is None:
        return HttpResponseForbidden()

    # Check if the user is a customer program execution manager for the customer
    # covered by test
    if not check__active_customer_program_execution_manager_contract__exists__between__employee_and_customer(
        employee=request.user.employee, customer=customer
    ):
        return HttpResponseForbidden()

    # Get the customer program execution
    # covered by test
    customer_program_execution = (
        get__customer_program_execution__for__customer_program_execution_id(
            customer_program_execution_id
        )
    )

    return render(
        request,
        "nadooit_os/customer_program_execution/components/complaint_modal.html",
        {
            "customer_program_execution": customer_program_execution,
        },
    )


@login_required(login_url="/auth/login-user")
@user_passes_test(
    user_is_Customer_Program_Execution_Manager, login_url="/auth/login-user"
)
def customer_program_execution_send_complaint(
    request: HttpRequest, customer_program_execution_id
):
    # check if the customer program execution exists
    # covered by test
    if not check__customer_program_execution__exists__for__customer_program_execution_id(
        customer_program_execution_id
    ):
        return HttpResponseForbidden()

    # Check that the user is a a customer program execution manager for the customer that the customer program execution belongs to
    # At this point we only know that the user is a customer program execution manager for a customer but we don't know if it is the customer that the customer program execution belongs to
    # since we do not want a user to be able to send a complaint for a customer program execution that does not belong to the customer that the user is a customer program execution manager for
    # we need to check that the user is a customer program execution manager for the customer that the customer program execution belongs to

    # Get the customer
    # covered by test
    customer = get__customer__for__customer_program_execution_id(
        customer_program_execution_id
    )

    if customer is None:
        return HttpResponseForbidden()

    # covered by test
    if not check__active_customer_program_execution_manager_contract__exists__between__employee_and_customer(
        employee=request.user.employee, customer=customer
    ):
        return HttpResponseForbidden()

    # Get the executions depending on the filter type
    # covered by test
    customer_program_execution = (
        get__customer_program_execution__for__customer_program_execution_id(
            customer_program_execution_id
        )
    )

    # Set the PaymentStatus for the customer program execution to "REVOKED"

    set__payment_status__for__customer_program_execution(
        customer_program_execution=customer_program_execution,
        payment_status="REVOKED",
    )

    # Create a complaint
    # covered by test
    if create__customer_program_execution_complaint__for__customer_program_execution_and_complaint_and_employee(
        customer_program_execution=customer_program_execution,
        complaint=request.POST["complainttext"],
        employee=request.user.employee,
    ):
        return HttpResponse("ok")
    else:
        return HttpResponse("error")


# login required and user must have the CustomerProgramExecutionManager role and can give the role
# does not use a form
@login_required(login_url="/auth/login-user")
@user_passes_test(
    user_is_Customer_Program_Execution_Manager_and_can_give_Customer_Program_Execution_Manager_role,
    login_url="/auth/login-user",
)
def give_customer_program_execution_manager_role(request: HttpRequest):
    submitted = False

    employee_with_customer_program_manager_contract = request.user.employee

    if request.method == "POST":

        user_code = request.POST.get("user_code")
        customer_id = request.POST.get("customer_id")
        list_of_abilities = request.POST.getlist("role")

        # guard clauses for the input data of the form (user_code, customer_id, list_of_abilities)

        # check that user_code is not empty
        # covered by test
        if not check__user__exists__for__user_code(user_code=user_code):
            return HttpResponseRedirect(
                "/nadooit-os/customer-program-execution/give-customer-program-execution-manager-role?submitted=True&error=Kein gültiger Benutzercode eingegeben"
            )

        # check that customer_id is not empty
        # covered by test
        if not check__customer__exists__for__customer_id(customer_id=customer_id):
            return HttpResponseRedirect(
                "/nadooit-os/customer-program-execution/give-customer-program-execution-manager-role?submitted=True&error=Kein gültiger Kunde eingegeben"
            )

        # covered by test
        customer = get__customer__for__customer_id(customer_id)

        # get the employee object for the user_code, checks not creates it
        # covered by test
        employee = get__employee__for__user_code(user_code=user_code)

        # covered by test
        if create__customer_program_execution_manager_contract__for__employee_and_customer_and_list_of_abilities_and_employee_with_customer_program_manager_contract(
            employee=employee,
            customer=customer,
            list_of_abilities=list_of_abilities,
            employee_with_customer_program_manager_contract=employee_with_customer_program_manager_contract,
        ):
            return HttpResponseRedirect(
                "/nadooit-os/customer-program-execution/give-customer-program-execution-manager-role?submitted=True"
            )

    else:
        if "submitted" in request.GET:
            submitted = True

    # covered by test
    list_of_customers_the_employee_has_a_customer_program_manager_contract_with_and_can_create_such_a_contract = get__list_of_customers_the_employee_has_a_customer_program_execution_manager_contract_with_and_can_create_such_a_contract(
        employee=employee_with_customer_program_manager_contract
    )

    return render(
        request,
        "nadooit_os/customer_program_execution/give_customer_program_execution_manager_role.html",
        {
            "page_title": "Programmausführungs Manager Rolle vergeben",
            "submitted": submitted,
            "error": request.GET.get("error"),
            "list_of_customers_the_manager_is_responsible_for": list_of_customers_the_employee_has_a_customer_program_manager_contract_with_and_can_create_such_a_contract,
            **get__user__roles_and_rights__for__http_request(request),
        },
    )


# Views for the customer program overview
@login_required(login_url="/auth/login-user")
@user_passes_test(user_is_Customer_Program_Manager, login_url="/auth/login-user")
def customer_program_overview(request: HttpRequest):

    # All orders for the current customer
    # orders are the executions of customerprograms

    # the list of customers that the time accounts that the employee is responsible for belong to
    # the list has for its first element the customer that the employee is responsible for
    # the list has for its second element the ccustomer programm execution for the customer that the employee is responsible for

    # covered by test
    customers_the_user_is_responsible_for_and_the_customer_programms = get__list_of_customers_the_employee_has_a_customer_programm_manager_contract_with_and_the_customer_programms__for__employee(
        employee=request.user.employee
    )

    # Multiple lists for the different order states
    # List one shows all orders for the current month
    # List shows all previous orders
    return render(
        request,
        "nadooit_os/customer_program/customer_program_overview.html",
        {
            "page_title": "Übersicht der Programme",
            "customers_the_user_is_responsible_for_and_the_customer_programms": customers_the_user_is_responsible_for_and_the_customer_programms,
            **get__user__roles_and_rights__for__http_request(request),
        },
    )


@require_POST
@user_passes_test(
    user_is_Customer_Program_Manager,
    login_url="/auth/login-user",
)
@login_required(login_url="/auth/login-user")
def get__customer_program_profile(
    request: HttpRequest, customer_program_id: str
) -> HttpResponse:
    # Check that the user is a a customer program  manager for the customer that the customer program belongs to
    # print("customer_program_id", customer_program_id)
    # covered by test
    if not check__customer_program__for__customer_program_id__exists(
        customer_program_id
    ):
        return HttpResponse(status=404)

    # Get the customer program
    # covered by test
    customer_program = get__customer_program__for__customer_program_id(
        customer_program_id
    )

    # covered by test
    if not check__user__is__customer_program_manager__for__customer_prgram(
        request.user,
        customer_program,
    ):
        return HttpResponseForbidden()

    # print("customer_program", customer_program)
    next_price = get__next_price_level__for__customer_program(customer_program)

    return render(
        request,
        "nadooit_os/customer_program/components/customer_program_profile.html",
        {
            "next_price": next_price,
            "customer_program": customer_program,
        },
    )


@login_required(login_url="/auth/login-user")
@user_passes_test(
    user_is_Customer_Program_Execution_Manager_and_can_give_Customer_Program_Execution_Manager_role,
    login_url="/auth/login-user",
)
def give_customer_program_manager_role(request: HttpRequest):
    submitted = False

    customer_program_manager_that_is_creating_the_contract = request.user.employee

    if request.method == "POST":

        user_code = request.POST.get("user_code")

        # check that user_code is not empty
        # covered by test
        if not check__user__exists__for__user_code(user_code):

            return HttpResponseRedirect(
                "/nadooit-os/cutomer-program/give-customer-program-manager-role?submitted=True&error=Kein gültiger Benutzercode eingegeben"
            )

        customer = request.POST.get("customers")

        # covered by test
        if not check__customer__exists__for__customer_id(customer):
            return HttpResponseRedirect(
                "/nadooit-os/cutomer-program/give-customer-program-manager-role?submitted=True&error=Kein gültiger Kunde eingegeben"
            )

        # covered by test
        customer = get__customer__for__customer_id(customer)

        # covered by test
        employee = get__employee__for__user_code(user_code)

        # covered by test
        customer_program_manager_contract = (
            get__customer_program_manager_contract__for__employee_and_customer(
                employee, customer
            )
        )

        # give the employee the roles that were selected and are stored in selected_abilities, the possible abilities are stored in the list of abilities
        # get the "role"
        list_of_selected_abilities = request.POST.getlist("role")

        # covered by test
        customer_program_manager_contract_of_employee_that_is_creating_the_contract = (
            get__customer_program_manager_contract__for__employee_and_customer(
                customer_program_manager_that_is_creating_the_contract, customer
            )
        )

        # covered by test
        list_of_abilities__for__customer_program_manager_contract_that_is_creating_the_new_contract = get__list_of_abilties__for__customer_program_manager_contract(
            customer_program_manager_contract_of_employee_that_is_creating_the_contract
        )

        # covered by test
        list_of_abilities_for_new_contract__for__selected_abilities_and_possible_abilities_the_employee_can_give = get__list_of_abilities__for__list_of_selected_abilities_and_list_of_possible_abilities_the_employee_can_give(
            list_of_possible_abilities=list_of_abilities__for__customer_program_manager_contract_that_is_creating_the_new_contract,
            list_of_selected_abilities=list_of_selected_abilities,
        )

        # covered by test
        set__list_of_abilities__for__customer_program_manager_contract_according_to_list_of_abilities(
            customer_program_manager_contract=customer_program_manager_contract,
            list_of_abilities=list_of_abilities_for_new_contract__for__selected_abilities_and_possible_abilities_the_employee_can_give,
        )

        return HttpResponseRedirect(
            "/nadooit-os/customer-program/give-customer-program-manager-role?submitted=True"
        )

    else:
        if "submitted" in request.GET:
            submitted = True

    # get the list of customers the customer program manager is responsible for
    # covered by test
    list_of_customers_the_manager_is_responsible_for = get__list_of_customers_the_employee_has_a_customer_program_manager_contract_with_and_can_create_such_a_contract(
        customer_program_manager_that_is_creating_the_contract
    )

    return render(
        request,
        "nadooit_os/customer_program/give_customer_program_manager_role.html",
        {
            "page_title": "Programm Manager Rolle vergeben",
            "submitted": submitted,
            "error": request.GET.get("error"),
            "list_of_customers_the_manager_is_responsible_for": list_of_customers_the_manager_is_responsible_for,
            **get__user__roles_and_rights__for__http_request(request),
        },
    )


# views for the hr department
@user_passes_test(user_is_Employee_Manager, login_url="/auth/login-user")
@login_required(login_url="/auth/login-user")
def employee_overview(request: HttpRequest):

    # This page displays all the employees that the logged in user is responsible for
    # The user can be the employee manager of multiple companies
    # Each company has multiple employees
    # The page displays all the employees of all the companies the user is responsible for as a lists
    # Each list is a company and the employees are the employees of that company
    # TODO missing the ability to deactiave the diactivate button if the user does not have the right to deactivate employees

    # TODO #113 test for this is not working. This structure could be restsrtuctured to make it easier to test
    customers__and__employees__for__employee_manager_contract__that_can_add_employees__for__user = get__list_of_customers__and__their_employees__for__customers_that_have_a_employee_manager_contract__for__user(
        request.user
    )

    return render(
        request,
        "nadooit_os/hr_department/employee_overview.html",
        {
            "page_title": "Mitarbeiter Übersicht",
            "customers__and__employees__for__employee_manager_contract__that_can_add_employees__for__user": customers__and__employees__for__employee_manager_contract__that_can_add_employees__for__user,
            **get__user__roles_and_rights__for__http_request(request),
        },
    )


@login_required(login_url="/auth/login-user")
def employee_profile(request: HttpRequest):

    logger.info("employee_profile view accessed")

    # def employee_profile(request: HttpRequest, employee_id: uuid4):
    # TODO This is not doen yet and can and should not be used

    # get the employee id from the current user
    employee_id = request.user.employee.id

    # get the employee object
    employee = get__employee__for__employee_id(employee_id)

    # A list of all the customers the user is responsible for so that in the profile the user only sees the infroation of the employee that is also part of the customers the user is responsible for
    list_of_all_employee_manager_contracts_of_the_user = (
        EmployeeManagerContract.objects.filter(contract__employee=request.user.employee)
    )
    customers_the_user_is_responsible_for = [
        employee_manager_contract.contract.customer
        for employee_manager_contract in list_of_all_employee_manager_contracts_of_the_user
    ]

    # check if the employee is part of the customers the user is responsible for. If not the user is not allowed to see the profile.
    if (
        EmployeeContract.objects.filter(
            employee=employee, customer__in=customers_the_user_is_responsible_for
        ).exists()
        == False
    ):
        return HttpResponseForbidden()

    # get the employee contracts of the employee that are part of the customers the user is responsible for
    employee_contracts_of_customers_the_user_is_responsible_for = (
        EmployeeContract.objects.filter(
            employee=employee, customer__in=customers_the_user_is_responsible_for
        )
    )

    user_info = get__user_info__for__user(employee.user)

    # Take the employee contracts and then get for each the employee manager contracts
    # Structure of the list:
    """ 
    
    list_of_employee_contracts = [
        {	
            "employee_contract": employee_contract, # the employee contract object
            "list_of_manager_contracts": [
                employee_manager_contract,
                customer_program_manager_contract,
            ],	
        },
        {
            "employee_contract": employee_contract, # the employee contract object	
            "list_of_manager_contracts": [	
                employee_manager_contract,
                customer_program_manager_contract,	
            ],		
        },                 
    ]	
    """

    list_of_employee_contracts = []

    list_of_employee_contracts = get__list_of_manager_contracts__for__employee(employee)

    logger.info(list_of_employee_contracts)

    return render(
        request,
        "nadooit_os/user_profile/user_profile.html",
        {
            "page_title": " Profil",
            "user_info": user_info,
            "list_of_employee_contracts": list_of_employee_contracts,
            **get__user__roles_and_rights__for__http_request(request),
        },
    )


@user_passes_test(
    user_is_Employee_Manager_and_can_add_new_employee, login_url="/auth/login-user"
)
@login_required(login_url="/auth/login-user")
def add_employee(request: HttpRequest):
    submitted = False
    if request.method == "POST":
        user_code = request.POST.get("user_code")
        customer_id = request.POST.get("customers")

        # check that user_code is not empty
        if not check__user__exists__for__user_code(user_code):
            return HttpResponseRedirect(
                "/nadooit-os/hr/add-employee?submitted=False&error=Kein gültiger Benutzercode eingegeben"
            )

        if not check__customer__exists__for__customer_id(customer_id):
            return HttpResponseRedirect(
                "/nadooit-os/hr/add-employee?submitted=False&error=Kein gültiger Kunde ausgewählt"
            )

        # covert by test
        customer = get__customer__for__customer_id(customer_id)

        # covert by test
        if not check__employee_manager_contract__exists__for__employee_manager_and_customer__and__can_add_users__and__is_active(
            request.user.employee, customer
        ):
            return HttpResponseRedirect(
                "/nadooit-os/hr/add-employee?submitted=False&error=Sie haben nicht die notwendige Berechtigung um einen Mitarbeiter für diesen Kunden hinzuzufügen"
            )
            # makes sure that there is a employee contract between the employee the selected customer

        # covert by test
        if get__employee_contract__for__user_code__and__customer(user_code, customer):
            return HttpResponseRedirect("/nadooit-os/hr/add-employee?submitted=True")

    else:
        if "submitted" in request.GET:
            submitted = True

    # get the list of customers the employee has a employee manager contract with that can add employees
    # covered by test
    list_of_customers_the_employee_has_a_employee_manager_contract_with_that_can_add_employees = get__list_of_customers__for__employee_manager_contract__that_can_add_employees__for__user(
        request.user
    )

    return render(
        request,
        "nadooit_os/hr_department/add_employee.html",
        {
            "submitted": submitted,
            "error": request.GET.get("error"),
            "page_title": "Mitarbeiter hinzufügen",
            "list_of_customers__for__employee_manager_contract": list_of_customers_the_employee_has_a_employee_manager_contract_with_that_can_add_employees,
            **get__user__roles_and_rights__for__http_request(request),
        },
    )


@user_passes_test(
    user_is_Employee_Manager_and_can_give_Employee_Manager_role,
    login_url="/auth/login-user",
)
@login_required(login_url="/auth/login-user")
def give_employee_manager_role(request: HttpRequest):

    employee_manager_giving_the_role = request.user.employee

    submitted = False
    if request.method == "POST":

        user_code = request.POST.get("user_code")
        list_of_abilities = request.POST.getlist("role")
        customer_id = request.POST.get("customers")

        # covert by test
        if not check__customer__exists__for__customer_id(customer_id):
            return HttpResponseRedirect(
                "/nadooit-os/hr/give-employee-manager-role?submitted=True&error=Kein valider Kunde."
            )

        # covert by test
        customer = get__customer__for__customer_id(customer_id)

        # check that user_code is not empty
        # covert by test
        if not check__user__exists__for__user_code(user_code):
            return HttpResponseRedirect(
                "/nadooit-os/hr/give-employee-manager-role?submitted=True&error=Kein gültiger Benutzercode eingegeben"
            )

        if (
            # covert by test
            create__employee_manager_contract__for__user_code_customer_and_list_of_abilities_according_to_employee_creating_contract(
                user_code, customer, list_of_abilities, employee_manager_giving_the_role
            )
            is not None
        ):
            return HttpResponseRedirect(
                "/nadooit-os/hr/give-employee-manager-role?submitted=True"
            )

    else:
        if "submitted" in request.GET:
            submitted = True

    # covert by test
    list_of_customers_the_manager_is_responsible_for = get__list_of_customers__for__employee_manager_contract__that_can_give_the_role__for__user(
        request.user
    )

    return render(
        request,
        "nadooit_os/hr_department/give_employee_manager_role.html",
        {
            "page_title": "Mitarbeiter Manager Rolle vergeben",
            "submitted": submitted,
            "error": request.GET.get("error"),
            "list_of_customers_the_manager_is_responsible_for": list_of_customers_the_manager_is_responsible_for,
            **get__user__roles_and_rights__for__http_request(request),
        },
    )


@require_POST
@user_passes_test(
    user_is_Employee_Manager_and_can_delete_employee,
    login_url="/auth/login-user",
)
@login_required(login_url="/auth/login-user")
def deactivate_contract(request: HttpRequest, employee_contract_id: str):

    # covert by test
    employee_contract = set_employee_contract__as_inactive__for__employee_contract_id(
        employee_contract_id
    )

    return render(
        request,
        "nadooit_os/hr_department/components/activate_contract_button.html",
        {
            "employee_contract": employee_contract,
        },
    )


@require_POST
@user_passes_test(
    user_is_Employee_Manager_and_can_delete_employee,
    login_url="/auth/login-user",
)
@login_required(login_url="/auth/login-user")
def activate_contract(request: HttpRequest, employee_contract_id: str):

    # covert by test
    set__employee_contract__is_active_state__for__employee_contract_id(
        employee_contract_id, True
    )

    # covert by test
    employee_contract = get__employee_contract__for__employee_contract_id(
        employee_contract_id
    )

    return render(
        request,
        "nadooit_os/hr_department/components/deactivate_contract_button.html",
        {
            "employee_contract": employee_contract,
        },
    )


# A view that creates a cvs file with all transactions for the given customer_id
@require_GET
@login_required(login_url="/auth/login-user")
def export_transactions(request: HttpRequest, filter_type, cutomer_id):

    # covert by test
    if not check__customer__exists__for__customer_id(cutomer_id):
        return HttpResponseNotFound("Customer not found")

    # covert by test
    cutomer = get__customer__for__customer_id(cutomer_id)

    unpaid_customer_program_executions = (
        # covert by test
        get__not_paid_customer_program_executions__for__filter_type_and_customer(
            filter_type, cutomer
        )
    )

    return get__csv__for__list_of_customer_program_executions(
        unpaid_customer_program_executions
    )
