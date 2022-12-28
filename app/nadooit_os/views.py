import csv
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import (
    HttpRequest,
    HttpResponseForbidden,
    HttpResponseNotFound,
    HttpResponseRedirect,
    HttpResponse,
)
from django.views.decorators.http import require_GET, require_POST
from django.shortcuts import render
from nadooit_os.services import (
    check__customer__exists__for__customer_id,
    get__not_paid_customer_program_executions__for__filter_type_and_customer,
)
from nadooit_os.services import (
    get__price_as_string_in_euro_format__for__price_in_euro_as_decimal,
)
from nadooit_os.services import (
    get__time_as_string_in_hour_format__for__time_in_seconds_as_integer,
)
from nadooit_os.services import (
    get__sum_of_price_for_execution__for__list_of_customer_program_exections,
)
from nadooit_os.services import (
    get__sum_of_time_saved_in_seconds__for__list_of_customer_program_exections,
)
from nadooit_os.services import (
    check__active_customer_program_execution_manager_contract__exists__between__employee_and_customer,
)
from nadooit_os.services import (
    get__list_of_customer_program_execution__for__employee_and_filter_type__grouped_by_customer,
)
from nadooit_os.services import (
    get__customer_program_executions__for__filter_type_and_customer,
)
from nadooit_os.services import (
    get__list_of_customers__for__employee_that_has_a_time_account_manager_contract_with_and_can_create_time_account_manager_contracts_for_them,
)
from nadooit_os.services import get__customer__for__customer_id
from nadooit_os.services import set__all_active_NadooitApiKey__for__user_to_inactive
from nadooit_os.services import create__NadooitApiKey__for__user
from nadooit_os.services import (
    get__customer_time_accounts_grouped_by_customer_with_total_time_of_all_time_accounts__for__employee,
)

from nadooit_auth.models import User

# Manager Roles
from nadooit_hr.models import (
    CustomerProgramExecutionManagerContract,
    CustomerProgramManagerContract,
    Employee,
    EmployeeManagerContract,
    TimeAccountManagerContract,
)
from nadooit_os.services import (
    check__user__exists__for__user_code,
    check__employee_manager_contract__for__user__can_deactivate__employee_contracts,
    check__employee_manager_contract__for__user__can_give_manager_role,
    create__time_account_manager_contract__for__user_code_customer_and_list_of_abilities_according_to_employee_creating_contract,
)
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
    if not check__customer__exists__for__customer_id(cutomer_id):
        return HttpResponseForbidden()
    # Get the customer
    customer = get__customer__for__customer_id(cutomer_id)

    # Check if the user is a customer program execution manager for the customer
    if (
        check__active_customer_program_execution_manager_contract__exists__between__employee_and_customer(
            employee=request.user.employee, customer=customer
        )
        is False
    ):
        return HttpResponseForbidden()

    # Get the executions depending on the filter type
    customer_program_executions = (
        get__customer_program_executions__for__filter_type_and_customer(
            filter_type, cutomer_id
        )
    )

    if filter_type == "last20":
        customer_program_executions = customer_program_executions[:20]

    total_time_saved_in_seconds = (
        get__sum_of_time_saved_in_seconds__for__list_of_customer_program_exections(
            customer_program_executions
        )
    )
    total_price_for_execution_decimal = (
        get__sum_of_price_for_execution__for__list_of_customer_program_exections(
            customer_program_executions
        )
    )
    total_time_saved = (
        get__time_as_string_in_hour_format__for__time_in_seconds_as_integer(
            total_time_saved_in_seconds
        )
    )
    # print("total_price_for_execution_decimal", total_price_for_execution_decimal)
    total_price_for_execution = (
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
    # Check that the user is a a customer program execution manager for the customer that the customer program execution belongs to
    if not CustomerProgramExecutionManagerContract.objects.filter(
        contract__employee=request.user.employee,
        contract__is_active=True,
        contract__customer=CustomerProgramExecution.objects.get(
            id=customer_program_execution_id
        ).customer_program.customer,
    ).exists():
        return HttpResponseForbidden()

    # Get the executions depending on the filter type
    customer_program_execution = CustomerProgramExecution.objects.get(
        id=customer_program_execution_id
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
    # Check that the user is a a customer program execution manager for the customer that the customer program execution belongs to
    if not CustomerProgramExecutionManagerContract.objects.filter(
        contract__employee=request.user.employee,
        contract__is_active=True,
        contract__customer=CustomerProgramExecution.objects.get(
            id=customer_program_execution_id
        ).customer_program.customer,
    ).exists():
        return HttpResponseForbidden()

    # Get the executions depending on the filter type
    customer_program_execution = CustomerProgramExecution.objects.get(
        id=customer_program_execution_id
    )

    # Set the PaymentStatus for the customer program execution to "REVOKED"
    customer_program_execution.payment_status = "REVOKED"
    customer_program_execution.save()

    # Create a complaint
    Complaint.objects.create(
        customer_program_execution=customer_program_execution,
        complaint=request.POST["complainttext"],
        customer_program_execution_manager=request.user.employee,
    )

    return HttpResponse("ok")


# login required and user must have the CustomerProgramExecutionManager role and can give the role
# does not use a form
@login_required(login_url="/auth/login-user")
@user_passes_test(
    user_is_Customer_Program_Execution_Manager_and_can_give_Customer_Program_Execution_Manager_role,
    login_url="/auth/login-user",
)
def give_customer_program_execution_manager_role(request: HttpRequest):
    submitted = False
    if request.method == "POST":
        user_code = request.POST.get("user_code")

        # check that user_code is not empty
        if User.objects.filter(user_code=user_code).exists():

            # check if there is an emplyee for that user code
            if not Employee.objects.filter(user__user_code=user_code).exists():
                # create new employee for the user_code
                Employee.objects.create(user=User.objects.get(user_code=user_code))

            # get the employee object for the user
            employee = Employee.objects.get(user__user_code=user_code)

            # check if the employee already has the role
            if not CustomerProgramExecutionManagerContract.objects.filter(
                contract__employee=employee
            ).exists():
                # Check if the employee has a contract with the customer
                if not EmployeeContract.objects.filter(employee=employee).exists():
                    EmployeeContract.objects.create(
                        employee=employee,
                        customer=Customer.objects.get(id=request.POST.get("customers")),
                    )
                # Check if there is more then one EmployeeContract for the employee
                elif (
                    EmployeeContract.objects.filter(
                        employee=employee,
                        customer=Customer.objects.get(id=request.POST.get("customers")),
                    ).count()
                    > 1
                ):
                    # TODO add a way to select the correct contract if there is more then one contract for the employee
                    # This is not needed yet because the employee manager can only create one contract for the employee. This should be changed in the future to allow the employee manager to create more then one contract for the employee
                    return HttpResponseRedirect(
                        "/nadooit-os/customer-program-execution/give-customer-program-execution-manager-role?submitted=True&error=Der Mitarbeiter hat mehr als einen Vertrag mit diesem Kunden."
                    )
                # create the CustomerProgramExecutionManager
                CustomerProgramExecutionManagerContract.objects.create(
                    contract=EmployeeContract.objects.get(employee=employee)
                )
            # give the employee the roles that were selected and are stored in selected_abilities, the possible abilities are stored in the list of abilities
            # get the "role"
            list_of_abilities = request.POST.getlist("role")
            for ability in list_of_abilities:
                # check if the employee already has the ability
                if ability == "can_create_customer_program_execution":
                    if CustomerProgramExecutionManagerContract.objects.filter(
                        contract__employee=request.user.employee,
                        can_create_customer_program_execution=True,
                    ).exists():
                        # Set the ability for the CustomerProgramExecutionManagerContract object to the value of the ability
                        CustomerProgramExecutionManagerContract.objects.filter(
                            contract__employee=employee
                        ).update(can_create_customer_program_execution=True)
                if ability == "can_delete_customer_program_execution":
                    if CustomerProgramExecutionManagerContract.objects.filter(
                        contract__employee=request.user.employee,
                        can_delete_customer_program_execution=True,
                    ).exists():
                        # Set the ability for the CustomerProgramExecutionManagerContract object to the value of the ability
                        CustomerProgramExecutionManagerContract.objects.filter(
                            contract__employee=employee
                        ).update(can_delete_customer_program_execution=True)
                if ability == "can_give_manager_role":
                    if CustomerProgramExecutionManagerContract.objects.filter(
                        contract__employee=request.user.employee,
                        can_give_manager_role=True,
                    ).exists():
                        # Set the ability for the CustomerProgramExecutionManager object to the value of the ability
                        CustomerProgramExecutionManagerContract.objects.filter(
                            contract__employee=employee
                        ).update(can_give_manager_role=True)

            return HttpResponseRedirect(
                "/nadooit-os/customer-program-execution/give-customer-program-execution-manager-role?submitted=True"
            )

        else:
            return HttpResponseRedirect(
                "/nadooit-os/customer-program-execution/give-customer-program-execution-manager-role?submitted=True&error=Kein gültiger Benutzercode eingegeben"
            )

    else:
        if "submitted" in request.GET:
            submitted = True

    list_of_customer_program_execution_manager_contract = (
        CustomerProgramExecutionManagerContract.objects.filter(
            contract__employee=request.user.employee, can_give_manager_role=True
        ).distinct("contract__customer")
    )

    # get the list of customers the customer program manager is responsible for using the list_of_customer_program_execution_manager_contract
    list_of_customers_the_manager_is_responsible_for = []
    for contract in list_of_customer_program_execution_manager_contract:
        list_of_customers_the_manager_is_responsible_for.append(
            contract.contract.customer
        )

    return render(
        request,
        "nadooit_os/customer_program_execution/give_customer_program_execution_manager_role.html",
        {
            "page_title": "Programmausführungs Manager Rolle vergeben",
            "submitted": submitted,
            "error": request.GET.get("error"),
            "list_of_customers_the_manager_is_responsible_for": list_of_customers_the_manager_is_responsible_for,
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
    customers_the_user_is_responsible_for_and_the_customer_programms = []

    list_of_customer_program_manger_contract_for_logged_in_user = (
        CustomerProgramManagerContract.objects.filter(
            contract__employee=request.user.employee, can_give_manager_role=True
        ).distinct("contract__customer")
    )

    # get the list of customers the customer program manager is responsible for using the list_of_customer_program_manger_contract_for_logged_in_user
    for contract in list_of_customer_program_manger_contract_for_logged_in_user:

        # list of customer programms with of the customer
        customer_programms = CustomerProgram.objects.filter(
            customer=contract.contract.customer
        )

        # add the customer and the customer programm execution to the list
        customers_the_user_is_responsible_for_and_the_customer_programms.append(
            [contract.contract.customer, customer_programms]
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

    if check__customer_program__for__customer_program_id__exists(customer_program_id):
        if not check__user__is__customer_program_manager__for__customer_prgram(
            request.user,
            get__customer_program__for__customer_program_id(customer_program_id),
        ):
            return HttpResponseForbidden()
    else:
        return HttpResponse(status=404)

    # Get the customer program
    customer_program = get__customer_program__for__customer_program_id(
        customer_program_id
    )
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
    if request.method == "POST":
        user_code = request.POST.get("user_code")

        # check that user_code is not empty
        if check__user__exists__for__user_code(user_code):

            # check if there is an emplyee for that user code
            if not Employee.objects.filter(user__user_code=user_code).exists():
                # create new employee for the user_code
                Employee.objects.create(user=User.objects.get(user_code=user_code))

            # get the employee object for the user
            employee = Employee.objects.get(user__user_code=user_code)

            # check if the employee already has the role
            if not CustomerProgramManagerContract.objects.filter(
                contract__employee=employee
            ).exists():
                # Check if the employee has a contract with the customer
                if not EmployeeContract.objects.filter(employee=employee).exists():
                    EmployeeContract.objects.create(
                        employee=employee,
                        customer=Customer.objects.get(id=request.POST.get("customers")),
                    )
                # Check if there is more then one EmployeeContract for the employee
                elif (
                    EmployeeContract.objects.filter(
                        employee=employee,
                        customer=Customer.objects.get(id=request.POST.get("customers")),
                    ).count()
                    > 1
                ):
                    # TODO add a way to select the correct contract if there is more then one contract for the employee
                    # This is not needed yet because the employee manager can only create one contract for the employee. This should be changed in the future to allow the employee manager to create more then one contract for the employee
                    return HttpResponseRedirect(
                        "/nadooit-os/customer-program/give-customer-program-manager-role?submitted=True&error=Der Mitarbeiter hat mehr als einen Vertrag mit diesem Kunden."
                    )
                # create the CustomerProgramManagerContract
                CustomerProgramManagerContract.objects.create(
                    contract=EmployeeContract.objects.get(employee=employee)
                )
            # give the employee the roles that were selected and are stored in selected_abilities, the possible abilities are stored in the list of abilities
            # get the "role"
            list_of_abilities = request.POST.getlist("role")
            for ability in list_of_abilities:
                # check if the employee already has the ability
                if ability == "can_create_customer_program":
                    if CustomerProgramManagerContract.objects.filter(
                        contract__employee=request.user.employee,
                        can_create_customer_program=True,
                    ).exists():
                        # Set the ability for the CustomerProgramManagerContract object to the value of the ability
                        CustomerProgramManagerContract.objects.filter(
                            contract__employee=employee
                        ).update(can_create_customer_program=True)
                if ability == "can_delete_customer_program":
                    if CustomerProgramManagerContract.objects.filter(
                        contract__employee=request.user.employee,
                        can_delete_customer_program=True,
                    ).exists():
                        # Set the ability for the CustomerProgramManagerContract object to the value of the ability
                        CustomerProgramManagerContract.objects.filter(
                            contract__employee=employee
                        ).update(can_delete_customer_program=True)
                if ability == "can_give_manager_role":
                    if CustomerProgramManagerContract.objects.filter(
                        contract__employee=request.user.employee,
                        can_give_manager_role=True,
                    ).exists():
                        # Set the ability for the CustomerProgramManagerContract object to the value of the ability
                        CustomerProgramManagerContract.objects.filter(
                            contract__employee=employee
                        ).update(can_give_manager_role=True)

            return HttpResponseRedirect(
                "/nadooit-os/customer-program/give-customer-program-manager-role?submitted=True"
            )

        else:
            return HttpResponseRedirect(
                "/nadooit-os/cutomer-program/give-customer-program-manager-role?submitted=True&error=Kein gültiger Benutzercode eingegeben"
            )

    else:
        if "submitted" in request.GET:
            submitted = True

    list_of_employee_manager_contract_for_logged_in_user = (
        CustomerProgramManagerContract.objects.filter(
            contract__employee=request.user.employee, can_give_manager_role=True
        ).distinct("contract__customer")
    )

    # get the list of customers the customer program manager is responsible for using the list_of_employee_manager_contract_for_logged_in_user
    list_of_customers_the_manager_is_responsible_for = []
    for contract in list_of_employee_manager_contract_for_logged_in_user:
        list_of_customers_the_manager_is_responsible_for.append(
            contract.contract.customer
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

    customers__and__employees__for__employee_manager_contract__that_can_add_employees__for__user = get__customers__and__employees__for__employee_manager_contract__that_can_add_employees__for__user(
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


@user_passes_test(user_is_Employee_Manager, login_url="/auth/login-user")
@login_required(login_url="/auth/login-user")
def employee_profile(request: HttpRequest, employee_id: int):
    # TODO This is not doen yet and can and should not be used

    # get the employee object
    employee = Employee.objects.get(id=employee_id)

    # A list of all the customers the user is responsible for so that in the profile the user only sees the infroation of the employee that is also part of the customers the user is responsible for
    customers_the_user_is_responsible_for = (
        request.user.employee.employeemanager.list_of_customers_the_manager_is_responsible_for.all()
    )

    # get the employee contracts of the employee that are part of the customers the user is responsible for
    employee_contracts_of_customers_the_user_is_responsible_for = (
        EmployeeContract.objects.filter(
            employee=employee, customer__in=customers_the_user_is_responsible_for
        )
    )

    return render(
        request,
        "nadooit_os/hr_department/employee_profile.html",
        {
            "page_title": "Mitarbeiter Profil",
            "employee": employee,
            "employee_contracts_of_customers_the_user_is_responsible_for": employee_contracts_of_customers_the_user_is_responsible_for,
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
        if check__user__exists__for__user_code(user_code):

            if check__customer__exists__for__customer_id(customer_id):

                if check__employee_manager_contract__exists__for__employee_manager_and_customer__and__can_add_users__and__is_active(
                    request.user.employee, customer_id
                ):
                    # makes sure that there is a employee contract between the employee the selected customer

                    if get__employee_contract__for__user_code__and__customer_id(
                        user_code, customer_id
                    ):
                        return HttpResponseRedirect(
                            "/nadooit-os/hr/add-employee?submitted=True"
                        )

                else:
                    return HttpResponseRedirect(
                        "/nadooit-os/hr/add-employee?submitted=False&error=Sie haben nicht die notwendige Berechtigung um einen Mitarbeiter für diesen Kunden hinzuzufügen"
                    )

            else:
                return HttpResponseRedirect(
                    "/nadooit-os/hr/add-employee?submitted=False&error=Kein gültiger Kunde ausgewählt"
                )

        else:
            return HttpResponseRedirect(
                "/nadooit-os/hr/add-employee?submitted=False&error=Kein gültiger Benutzercode eingegeben"
            )

    else:
        if "submitted" in request.GET:
            submitted = True

    return render(
        request,
        "nadooit_os/hr_department/add_employee.html",
        {
            "submitted": submitted,
            "page_title": "Mitarbeiter hinzufügen",
            "list_of_customers__for__employee_manager_contract": get__list_of_customers__for__employee_manager_contract__that_can_add_employees__for__user(
                request.user
            ),
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

        if check__more_then_one_contract_between__user_code__and__customer_id(
            user_code, customer_id
        ):
            # TODO add a way to select the correct contract if there is more then one contract for the employee
            # This is not needed yet because the employee manager can only create one contract for the employee. This should be changed in the future to allow the employee manager to create more then one contract for the employee
            return HttpResponseRedirect(
                "/nadooit-os/hr/give-employee-manager-role?submitted=True&error=Der Mitarbeiter hat mehr als einen Vertrag mit diesem Kunden."
            )

        employee_manager_contract = None

        # check that user_code is not empty
        if check__user__exists__for__user_code(user_code):

            employee_manager_contract = (
                get__employee_manager_contract__for__user_code__and__customer_id(
                    user_code, customer_id
                )
            )

            # give the employee the roles that were selected and are stored in selected_abilities, the possible abilities are stored in the list of abilities
            # get the "role"

            # TODO split the form for asking for the abities so that it shows the abilites for the active employee manager contract so that the employee manager can only give the abilities that are allowed for the contract
            # sets the abilities for the employee manager
            for ability in list_of_abilities:
                # check if the employee already has the ability
                if ability == "can_add_new_employee":
                    if EmployeeManagerContract.objects.filter(
                        contract__employee=employee_manager_giving_the_role,
                        contract__customer=employee_manager_contract.contract.customer,
                        can_add_new_employee=True,
                    ).exists():
                        # Set the ability for the EmployeeManagerContract object to the value of the ability
                        employee_manager_contract.can_add_new_employee = True
                if ability == "can_delete_employee":
                    if EmployeeManagerContract.objects.filter(
                        contract__employee=employee_manager_giving_the_role,
                        contract__customer=employee_manager_contract.contract.customer,
                        can_delete_employee=True,
                    ).exists():
                        # Set the ability for the EmployeeManagerContract object to the value of the ability
                        employee_manager_contract.can_delete_employee = True
                if ability == "can_give_manager_role":
                    if EmployeeManagerContract.objects.filter(
                        contract__employee=employee_manager_giving_the_role,
                        contract__customer=employee_manager_contract.contract.customer,
                        can_give_manager_role=True,
                    ).exists():
                        # Set the ability for the EmployeeManagerContract object to the value of the ability
                        employee_manager_contract.can_give_manager_role = True

                employee_manager_contract.save()

            return HttpResponseRedirect(
                "/nadooit-os/hr/give-employee-manager-role?submitted=True"
            )

        else:

            return HttpResponseRedirect(
                "/nadooit-os/hr/give-employee-manager-role?submitted=True&error=Kein gültiger Benutzercode eingegeben"
            )

    else:
        if "submitted" in request.GET:
            submitted = True

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

    set__employee_contract__is_active_state__for__employee_contract_id(
        employee_contract_id, True
    )

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

    if not check__customer__exists__for__customer_id(cutomer_id):
        return HttpResponseNotFound("Customer not found")

    cutomer = get__customer__for__customer_id(cutomer_id)

    unpaid_customer_program_executions = (
        get__not_paid_customer_program_executions__for__filter_type_and_customer(
            filter_type, cutomer
        )
    )

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="transactions.csv"'

    writer = csv.writer(response)

    # write the header
    writer.writerow(["id", "Programmname", "erspaarte Zeit", "Preis", "Erstellt"])

    for transaction in unpaid_customer_program_executions:

        writer.writerow(
            [
                transaction.id,
                transaction.customer_program.program.name,
                transaction.program_time_saved_in_seconds,
                transaction.price_for_execution,
                transaction.created_at,
            ]
        )
    # return the response object
    return response
