from django.utils import timezone
from django.shortcuts import render

# imoport for userforms

from django.http import HttpRequest, HttpResponseRedirect
from requests import request

from nadooit_hr.models import CustomerProgramManagerContract
from .forms import ApiKeyForm, ApiKeyManagerForm, CustomerTimeAccountManagerForm
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# model imports
from nadooit_program_ownership_system.models import CustomerProgram
from nadooit_time_account.models import CustomerTimeAccount
from nadooit_api_key.models import NadooitApiKey
from nadooit_api_executions_system.models import CustomerProgramExecution
from nadooit_crm.models import Customer
from nadooit_auth.models import User
from nadooit_time_account.models import (
    get_time_as_string_in_hour_format_for_time_in_seconds_as_integer,
)
from nadooit_hr.models import Employee
from nadooit_hr.models import EmployeeContract

# Manager Roles
from nadooit_hr.models import EmployeeManagerContract
from nadooit_time_account.models import TimeAccountManager
from nadooit_api_executions_system.models import CustomerProgramExecutionManager
from nadooit_api_key.models import NadooitApiKeyManager


from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.decorators import login_required


# Tests for user roles

# Tests for Time Account Manager
def user_is_Time_Account_Manager(user: User) -> bool:
    if hasattr(user.employee, "timeaccountmanager"):
        return True
    return False


def user_is_Time_Account_Manager_and_can_give_manager_role(
    user: User,
) -> bool:
    if hasattr(user.employee, "timeaccountmanager"):
        if user.employee.timeaccountmanager.can_give_manager_role:
            return True
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
    if hasattr(user.employee, "customerprogramexecutionmanager"):
        return True
    return False


def user_is_Customer_Program_Execution_Manager_and_can_give_Customer_Program_Execution_Manager_role(
    user: User,
) -> bool:
    if hasattr(user.employee, "customerprogramexecutionmanager"):
        if user.employee.customerprogramexecutionmanager.can_give_manager_role:
            return True
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
    if EmployeeManagerContract.objects.filter(
        contract__employee=user.employee,
        contract__is_active=True,
        can_give_manager_role=True,
    ).exists():
        return True
    else:
        return False


def user_is_Employee_Manager_and_can_can_add_new_employee(
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


# Getting the user roles
# If new roles are added, they need to be added here
# this function uses the user_is_... functions above
def get__user__roles_and_rights(request: HttpRequest) -> dict:
    return {
        "is_time_account_manager": user_is_Time_Account_Manager(request.user),
        "user_is_Time_Account_Manager_and_can_give_manager_role": user_is_Time_Account_Manager_and_can_give_manager_role(
            request.user
        ),
        "is_api_key_manager": user_is_Api_Key_Manager(request.user),
        "user_is_api_key_manager_and_can_give_manager_role": user_is_Api_Key_Manager_and_can_give_manager_role(
            request.user
        ),
        "is_employee_manager": user_is_Employee_Manager(request.user),
        "user_is_Employee_Manager_and_can_give_Employee_Manager_role": user_is_Employee_Manager_and_can_give_Employee_Manager_role(
            request.user
        ),
        "user_is_Employee_Manager_and_can_can_add_new_employee": user_is_Employee_Manager_and_can_can_add_new_employee(
            request.user
        ),
        "is_customer_program_manager": user_is_Customer_Program_Manager(request.user),
        "user_is_Customer_Program_Manager_and_can_give_Customer_Program_Manager_role": user_is_Customer_Program_Manager_and_can_give_Customer_Program_Manager_role(
            request.user
        ),
        "is_customer_program_execution_manager": user_is_Customer_Program_Execution_Manager(
            request.user
        ),
        "user_is_Customer_Program_Execution_Manager_and_can_give_Customer_Program_Execution_Manager_role": user_is_Customer_Program_Execution_Manager_and_can_give_Customer_Program_Execution_Manager_role(
            request.user
        ),
    }


# Create your views here.
# Main page of the nadooit_os
@login_required(login_url="/auth/login-user")
def index_nadooit_os(request: HttpRequest):

    return render(
        request,
        "nadooit_os/index.html",
        # context as dict
        # first item is page_title
        # dict from get__user__roles_and_rights is added
        {
            "page_title": "Nadooit OS",
            **get__user__roles_and_rights(request),
        },
    )


# Views for the time account system
@login_required(login_url="/auth/login-user")
@user_passes_test(user_is_Time_Account_Manager, login_url="/auth/login-user")
def customer_time_account_overview(request: HttpRequest):

    time_accounts_the_user_is_responsible_for = list(
        TimeAccountManager.objects.get(
            employee=Employee.objects.get(user=request.user)
        ).time_accounts.all()
    )
    list_of_customer_time_accounts = []

    for time_account in time_accounts_the_user_is_responsible_for:
        # get the customertimeaccount for the time account
        customer_time_account = CustomerTimeAccount.objects.get(
            time_account=time_account
        )
        list_of_customer_time_accounts.append(customer_time_account)

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
    customer_time_accounts_grouped_by_customer = {}
    for customer_time_account in list_of_customer_time_accounts:
        if customer_time_account.customer in customer_time_accounts_grouped_by_customer:
            customer_time_accounts_grouped_by_customer[customer_time_account.customer][
                "customer_time_accounts"
            ].append(customer_time_account)
            customer_time_accounts_grouped_by_customer[customer_time_account.customer][
                "customer_time_account_total_time_balance"
            ] += customer_time_account.time_account.time_balance_in_seconds
        else:
            customer_time_accounts_grouped_by_customer[
                customer_time_account.customer
            ] = {
                "customer_time_accounts": [customer_time_account],
                "customer_time_account_total_time_balance": customer_time_account.time_account.time_balance_in_seconds,
            }

    print(customer_time_accounts_grouped_by_customer)

    # format the time balances first to int then using the get_time_as_string_in_hour_format_for_time_in_seconds_as_integer function
    for customer in customer_time_accounts_grouped_by_customer:
        customer_time_accounts_grouped_by_customer[customer][
            "customer_time_account_total_time_balance"
        ] = get_time_as_string_in_hour_format_for_time_in_seconds_as_integer(
            int(
                customer_time_accounts_grouped_by_customer[customer][
                    "customer_time_account_total_time_balance"
                ]
            )
        )

    # format the time balances for each customer time account
    for customer in customer_time_accounts_grouped_by_customer:
        for customer_time_account in customer_time_accounts_grouped_by_customer[
            customer
        ]["customer_time_accounts"]:
            customer_time_account.time_account.time_balance_in_seconds = (
                get_time_as_string_in_hour_format_for_time_in_seconds_as_integer(
                    int(customer_time_account.time_account.time_balance_in_seconds)
                )
            )

    return render(
        request,
        "nadooit_os/time_account/customer_time_account_overview.html",
        {
            "page_title": "Übersicht der Zeitkonten",
            "customer_time_accounts_grouped_by_customer": customer_time_accounts_grouped_by_customer,
            **get__user__roles_and_rights(request),
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
            new_api_key = NadooitApiKey(
                api_key=form.cleaned_data["api_key"],
                user=form.cleaned_data["user_code"],
                is_active=form.cleaned_data["is_active"],
            )
            new_api_key.updated_at = timezone.now()
            new_api_key.created_at = timezone.now()
            new_api_key.save()
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
            **get__user__roles_and_rights(request),
        },
    )


@login_required(login_url="/auth/login-user")
def revoke_api_key(request: HttpRequest):

    submitted = False
    if request.method == "POST":
        # get list of all api keys that are active for the user and set them to inactive
        api_keys = NadooitApiKey.objects.filter(user=request.user, is_active=True)
        for api_key in api_keys:
            api_key.is_active = False
            api_key.save()
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
            **get__user__roles_and_rights(request),
        },
    )


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
            **get__user__roles_and_rights(request),
        },
    )


@login_required(login_url="/auth/login-user")
@user_passes_test(
    user_is_Time_Account_Manager_and_can_give_manager_role,
    login_url="/auth/login-user",
)
def give_customer_time_account_manager_role(request: HttpRequest):
    submitted = False
    if request.method == "POST":
        form = CustomerTimeAccountManagerForm(
            request.POST,
        )

        if form.is_valid():

            user_code = form.cleaned_data["user_code"]
            # get the employee object for the user
            employee = Employee.objects.get(user__user_code=user_code)

            customers_the_new_manager_is_responsible_for = request.POST.getlist(
                "customers"
            )
            can_create_time_accounts = form.cleaned_data["can_create_time_accounts"]
            can_delete_time_accounts = form.cleaned_data["can_delete_time_accounts"]
            can_give_manager_role = form.cleaned_data["can_give_manager_role"]

            # check if the user is already an TimeAccountManager
            if user_is_Time_Account_Manager(employee.user):
                # if the employee is already an ApiKeyManager, update the existing ApiKeyManager object but only give more rights
                api_key_manager = TimeAccountManager.objects.get(employee=employee)
                if can_create_time_accounts == True:
                    api_key_manager.can_create_time_accounts = True

                if can_delete_time_accounts == True:
                    api_key_manager.can_delete_time_accounts = True

                if can_give_manager_role == True:
                    api_key_manager.can_give_manager_role = True

                api_key_manager.save()

            else:

                # create new api key manager
                new_time_account_manager = TimeAccountManager.objects.create(
                    employee=employee,
                    can_create_time_accounts=can_create_time_accounts,
                    can_delete_time_accounts=can_delete_time_accounts,
                    can_give_manager_role=can_give_manager_role,
                )

                # add the customers the new manager is responsible for
                for customer in customers_the_new_manager_is_responsible_for:
                    new_time_account_manager.list_of_customers_the_manager_is_responsible_for.add(
                        customer
                    )
                new_time_account_manager.save()

            return HttpResponseRedirect(
                "/nadooit-os/give-api-key-manager-role?submitted=True"
            )

    else:
        form = CustomerTimeAccountManagerForm(
            request.POST,
        )
        if "submitted" in request.GET:
            submitted = True

    form = CustomerTimeAccountManagerForm(
        request.POST,
    )

    list_of_customers_the_manager_is_responsible_for = (
        request.user.employee.timeaccountmanager.list_of_customers_the_manager_is_responsible_for.all()
    )
    time_accounts_the_manager_is_responsible_for = (
        request.user.employee.timeaccountmanager.time_accounts.all()
    )

    return render(
        request,
        "nadooit_os/time_account/give_customer_time_account_manager_role.html",
        {
            "page_title": "Zeitkonten Manager Rolle vergeben",
            "form": form,
            "submitted": submitted,
            "list_of_customers_the_manager_is_responsible_for": list_of_customers_the_manager_is_responsible_for,
            "time_accounts_the_manager_is_responsible_for": time_accounts_the_manager_is_responsible_for,
            **get__user__roles_and_rights(request),
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

    # the employee is the logged in user
    employee = Employee.objects.get(user=request.user)

    # the list of customers that the time accounts that the employee is responsible for belong to
    # the list has for its first element the customer that the employee is responsible for
    # the list has for its second element the ccustomer programm execution for the customer that the employee is responsible for
    customers_the_employee_is_responsible_for_and_the_customer_programm_executions = []

    for (
        customer_the_employe_works_for
    ) in (
        employee.customerprogramexecutionmanager.list_of_customers_the_manager_is_responsible_for.all()
    ):
        # list of customer programms with of the customer
        customer_programms = CustomerProgram.objects.filter(
            customer=customer_the_employe_works_for
        )
        # list of customer programm executions for the customer programm
        customer_programm_executions = list(
            CustomerProgramExecution.objects.filter(
                customer_program__in=customer_programms
            )
        )
        # add the customer and the customer programm execution to the list
        customers_the_employee_is_responsible_for_and_the_customer_programm_executions.append(
            [customer_the_employe_works_for, customer_programm_executions]
        )

    # Multiple lists for the different order states
    # List one shows all orders for the current month
    # List shows all previous orders
    print(
        customers_the_employee_is_responsible_for_and_the_customer_programm_executions
    )
    return render(
        request,
        "nadooit_os/customer_program_execution/customer_program_execution_overview.html",
        {
            "page_title": "Übersicht der Buchungen",
            "customers_the_user_is_responsible_for_and_the_customer_programm_executions": customers_the_employee_is_responsible_for_and_the_customer_programm_executions,
            **get__user__roles_and_rights(request),
        },
    )


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
            if Employee.objects.filter(user__user_code=user_code).exists():

                # get the employee object for the user
                employee = Employee.objects.get(user__user_code=user_code)

                # check if the user is already an CustomerProgramExecutionManager
                if user_is_Customer_Program_Execution_Manager(employee.user):
                    # if the employee is already an CustomerProgramExecutionManager, update the existing CustomerProgramExecutionManager object but only give more rights
                    customer_program_execution_manager = (
                        CustomerProgramExecutionManager.objects.get(employee=employee)
                    )
                    if request.POST.get("can_create_program_execution") == "True":
                        customer_program_execution_manager.can_create_program_execution = (
                            True
                        )

                    if request.POST.get("can_delete_program_execution") == "True":
                        customer_program_execution_manager.can_delete_program_execution = (
                            True
                        )

                    if request.POST.get("can_give_manager_role") == "True":
                        customer_program_execution_manager.can_give_manager_role = True

                    customer_program_execution_manager.save()

                else:

                    # create new customer program execution manager
                    new_customer_program_execution_manager = (
                        CustomerProgramExecutionManager.objects.create(
                            employee=employee,
                            can_create_program_execution=request.POST.get(
                                "can_create_program_execution"
                            )
                            == "True",
                            can_delete_program_execution=request.POST.get(
                                "can_delete_program_execution"
                            )
                            == "True",
                            can_give_manager_role=request.POST.get(
                                "can_give_manager_role"
                            )
                            == "True",
                        )
                    )

                    # add the customers the new manager is responsible for
                    for customer in request.POST.getlist("customers"):
                        new_customer_program_execution_manager.list_of_customers_the_manager_is_responsible_for.add(
                            customer
                        )
                    new_customer_program_execution_manager.save()

                return HttpResponseRedirect(
                    "/nadooit-os/customer-program-execution/give-customer-program-execution-manager-role?submitted=True"
                )

            else:
                return HttpResponseRedirect(
                    "/nadooit-os/customer-program-execution/give-customer-program-execution-manager-role?submitted=True&error=Benutzercode ist nicht als Mitarbeiter registriert"
                )

        else:
            return HttpResponseRedirect(
                "/nadooit-os/customer-program-execution/give-customer-program-execution-manager-role?submitted=True&error=Kein gültiger Benutzercode eingegeben"
            )

    else:
        if "submitted" in request.GET:
            submitted = True

    list_of_customers_the_manager_is_responsible_for = (
        request.user.employee.customerprogramexecutionmanager.list_of_customers_the_manager_is_responsible_for.all()
    )

    return render(
        request,
        "nadooit_os/customer_program_execution/give_customer_program_execution_manager_role.html",
        {
            "page_title": "Programmausführungs Manager Rolle vergeben",
            "submitted": submitted,
            "error": request.GET.get("error"),
            "list_of_customers_the_manager_is_responsible_for": list_of_customers_the_manager_is_responsible_for,
            "can_create_customer_program_execution": request.user.employee.customerprogramexecutionmanager.can_create_customer_program_execution,
            "can_delete_customer_program_execution": request.user.employee.customerprogramexecutionmanager.can_delete_customer_program_execution,
            "can_give_manager_role": request.user.employee.customerprogramexecutionmanager.can_give_manager_role,
            **get__user__roles_and_rights(request),
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
            **get__user__roles_and_rights(request),
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
        if User.objects.filter(user_code=user_code).exists():

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
            **get__user__roles_and_rights(request),
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
    customers_the_user_is_responsible_for_and_the_customers_employees = []

    # get all the customers the user is responsible for
    employee = Employee.objects.get(user=request.user)

    # get all the customers the employee has contracts with and is an employee manager for
    # Do not use employee.employeemanager.list_of_customers_the_manager_is_responsible_for.all()!
    # Instead look at the contracts the employee has and get the customers from the contracts
    # This is because the employee manager will be deprecated in the future
    # Only list a customer once

    list_of_customers_the_employee_has_an_employee_manager_contract_with = (
        EmployeeManagerContract.objects.filter(contract__employee=employee).distinct(
            "contract__customer"
        )
    )

    # get all the employees of the customers the user is responsible for
    for (
        customer
    ) in list_of_customers_the_employee_has_an_employee_manager_contract_with:
        customers_the_user_is_responsible_for_and_the_customers_employees.append(
            [
                customer.contract.customer,
                Employee.objects.filter(
                    employeecontract__customer=customer.contract.customer
                ).distinct(),
            ]
        )

    return render(
        request,
        "nadooit_os/hr_department/employee_overview.html",
        {
            "page_title": "Mitarbeiter Übersicht",
            "customers_the_user_is_responsible_for_and_the_customers_employees": customers_the_user_is_responsible_for_and_the_customers_employees,
            **get__user__roles_and_rights(request),
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
            **get__user__roles_and_rights(request),
        },
    )


@user_passes_test(
    user_is_Employee_Manager_and_can_can_add_new_employee, login_url="/auth/login-user"
)
@login_required(login_url="/auth/login-user")
def add_employee(request: HttpRequest):
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

            # Create a new employee contract for the employee between selected customers and the employee
            for customer in request.POST.getlist("customers"):

                # check if the employee already has a contract with the customer
                if not EmployeeContract.objects.filter(
                    employee=employee, customer=customer
                ).exists():
                    EmployeeContract.objects.create(
                        employee=employee,
                        customer=Customer.objects.get(id=customer),
                    )
            return HttpResponseRedirect("/nadooit-os/hr/add-employee?submitted=True")

        else:
            return HttpResponseRedirect(
                "/nadooit-os/hr/add-employee?submitted=True&error=Kein gültiger Benutzercode eingegeben"
            )

    else:
        if "submitted" in request.GET:
            submitted = True

    list_of_employee_manager_contract_for_logged_in_user = (
        EmployeeManagerContract.objects.filter(
            contract__employee=request.user.employee, can_add_new_employee=True
        ).distinct("contract__customer")
    )

    # get the list of customers the employee manager is responsible for using the list_of_employee_manager_contract_for_logged_in_user
    list_of_customers_the_manager_is_responsible_for = []
    for contract in list_of_employee_manager_contract_for_logged_in_user:
        list_of_customers_the_manager_is_responsible_for.append(
            contract.contract.customer
        )

    return render(
        request,
        "nadooit_os/hr_department/add_employee.html",
        {
            "submitted": submitted,
            "page_title": "Mitarbeiter hinzufügen",
            "list_of_customers_the_manager_is_responsible_for": list_of_customers_the_manager_is_responsible_for,
            **get__user__roles_and_rights(request),
        },
    )


@user_passes_test(
    user_is_Employee_Manager_and_can_give_Employee_Manager_role,
    login_url="/auth/login-user",
)
@login_required(login_url="/auth/login-user")
def give_employee_manager_role(request: HttpRequest):
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
            if not EmployeeManagerContract.objects.filter(
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
                        "/nadooit-os/hr/give-employee-manager-role?submitted=True&error=Der Mitarbeiter hat mehr als einen Vertrag mit diesem Kunden."
                    )
                # create the EmployeeManagerContract
                EmployeeManagerContract.objects.create(
                    contract=EmployeeContract.objects.get(employee=employee)
                )
            # give the employee the roles that were selected and are stored in selected_abilities, the possible abilities are stored in the list of abilities
            # get the "role"
            list_of_abilities = request.POST.getlist("role")
            print(list_of_abilities)
            for ability in list_of_abilities:
                # check if the employee already has the ability
                if ability == "can_add_new_employee":
                    if EmployeeManagerContract.objects.filter(
                        contract__employee=request.user.employee,
                        can_add_new_employee=True,
                    ).exists():
                        # Set the ability for the EmployeeManagerContract object to the value of the ability
                        EmployeeManagerContract.objects.filter(
                            contract__employee=employee
                        ).update(can_add_new_employee=True)
                if ability == "can_delete_employee":
                    if EmployeeManagerContract.objects.filter(
                        contract__employee=request.user.employee,
                        can_delete_employee=True,
                    ).exists():
                        # Set the ability for the EmployeeManagerContract object to the value of the ability
                        EmployeeManagerContract.objects.filter(
                            contract__employee=employee
                        ).update(can_delete_employee=True)
                if ability == "can_give_manager_role":
                    if EmployeeManagerContract.objects.filter(
                        contract__employee=request.user.employee,
                        can_give_manager_role=True,
                    ).exists():
                        # Set the ability for the EmployeeManagerContract object to the value of the ability
                        EmployeeManagerContract.objects.filter(
                            contract__employee=employee
                        ).update(can_give_manager_role=True)

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

    list_of_employee_manager_contract_for_logged_in_user = (
        EmployeeManagerContract.objects.filter(
            contract__employee=request.user.employee, can_give_manager_role=True
        ).distinct("contract__customer")
    )

    # get the list of customers the employee manager is responsible for using the list_of_employee_manager_contract_for_logged_in_user
    list_of_customers_the_manager_is_responsible_for = []
    for contract in list_of_employee_manager_contract_for_logged_in_user:
        list_of_customers_the_manager_is_responsible_for.append(
            contract.contract.customer
        )

    print(list_of_customers_the_manager_is_responsible_for)
    return render(
        request,
        "nadooit_os/hr_department/give_employee_manager_role.html",
        {
            "page_title": "Mitarbeiter Manager Rolle vergeben",
            "submitted": submitted,
            "error": request.GET.get("error"),
            "list_of_customers_the_manager_is_responsible_for": list_of_customers_the_manager_is_responsible_for,
            **get__user__roles_and_rights(request),
        },
    )
