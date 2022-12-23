import decimal
from decimal import Decimal
import math
from typing import List, Union
import hashlib
import uuid

from django.utils import timezone
from nadooit_time_account.models import (
    get_time_as_string_in_hour_format_for_time_in_seconds_as_integer,
)
from nadooit_time_account.models import CustomerTimeAccount
from nadooit_hr.models import TimeAccountManagerContract
from nadooit_time_account.models import TimeAccount
from nadooit_hr.models import CustomerProgramManagerContract

from nadooit_program_ownership_system.models import CustomerProgram

from nadooit_api_key.models import NadooitApiKey
from nadooit_api_executions_system.models import CustomerProgramExecution
from nadooit_crm.models import Customer
from nadooit_hr.models import EmployeeManagerContract
from nadooit_hr.models import Employee
from nadooit_hr.models import EmployeeContract
from nadooit_auth.models import User
from datetime import datetime
from django.db.models import QuerySet


def get__not_paid_customer_program_executions__for__filter_type_and_cutomer_id(
    filter_type, cutomer_id
):
    customer_program_executions = (
        get__customer_program_executions__for__filter_type_and_cutomer_id(
            filter_type, cutomer_id
        ).filter(payment_status="NOT_PAID")
    )
    return customer_program_executions


def get__customer_program_executions__for__filter_type_and_cutomer_id(
    filter_type, cutomer_id
):
    from datetime import date

    todays_date = date.today()
    customer_program_executions = None
    if filter_type == "lastmonth":

        print(todays_date.month)
        print(todays_date.month - 1)

        customer_program_executions = (
            CustomerProgramExecution.objects.filter(
                customer_program__customer__id=cutomer_id,
                created_at__month=todays_date.month - 1,
            )
            .order_by("created_at")
            .reverse()
        )
    elif filter_type == "today":
        customer_program_executions = (
            CustomerProgramExecution.objects.filter(
                customer_program__customer__id=cutomer_id, created_at__date=todays_date
            )
            .order_by("created_at")
            .reverse()
        )
    elif filter_type == "last20":
        customer_program_executions = (
            CustomerProgramExecution.objects.filter(
                customer_program__customer__id=cutomer_id
            )
            .order_by("created_at")
            .reverse()
        )
    elif filter_type == "thismonth":
        customer_program_executions = (
            CustomerProgramExecution.objects.filter(
                customer_program__customer__id=cutomer_id,
                created_at__month=todays_date.month,
            )
            .order_by("created_at")
            .reverse()
        )
    elif filter_type == "thisyear":
        customer_program_executions = (
            CustomerProgramExecution.objects.filter(
                customer_program__customer__id=cutomer_id,
                created_at__year=todays_date.year,
            )
            .order_by("created_at")
            .reverse()
        )
    return customer_program_executions


def get__price_as_string_in_euro_format__for__price_in_euro_as_decimal(price) -> str:
    """
    Returns the price as a string in euro format
    """
    if price is None:
        price = 0

    price_as_string = f"{round(price, 3):.3f}"
    price_as_string = price_as_string.replace(".", ",")

    if price_as_string.endswith(",0"):
        price_as_string = price_as_string[:-1]

    return f"{price_as_string} €"


def get__time_as_string_in_hour_format__for__time_in_seconds_as_integer(time) -> str:
    # The format of the final string should result in something like this "25 std : 03 min : 05 sek"
    return f"{math.floor(time / 3600)} std : {math.floor((time % 3600) / 60)} min : {math.floor(time % 60)} sek"


# Refactore this function because it requeres an employee and not a user. This is dangerous because it is not clear by the name of the function
def check__user__is__customer_program_manager__for__customer_prgram(
    user, customer_program
):
    return CustomerProgramManagerContract.objects.filter(
        contract__employee=user.employee,
        contract__is_active=True,
        contract__customer=customer_program.customer,
    ).exists()


def check__customer_program__for__customer_program_id__exists(customer_program_id):
    return CustomerProgram.objects.filter(id=customer_program_id).exists()


def get__customer_program__for__customer_program_id(customer_program_id):
    return CustomerProgram.objects.get(id=customer_program_id)


# Checks if a user exists for the given user code
def check__user__exists__for__user_code(user_code) -> bool:
    return User.objects.filter(user_code=user_code).exists()


# Sets the employee contract as the given state
def set__employee_contract__is_active_state__for__employee_contract_id(
    employee_contract_id, contract_state
) -> EmployeeContract:

    employee_contract = get__employee_contract__for__employee_contract_id(
        employee_contract_id
    )
    employee_contract.is_active = contract_state

    # If the contract is set to active, set the deactivation date to null
    employee_contract.deactivation_date = None
    employee_contract.save()

    # returns the changed employee contract
    return employee_contract


# Returns the employee contract for the given employee contract id
def get__employee_contract__for__employee_contract_id(
    employee_contract_id,
) -> EmployeeContract:
    employee_contract = EmployeeContract.objects.get(id=employee_contract_id)
    return employee_contract


# Sets the deactivation date of a employee contract for the given employee contract id
def set__employee_contract__deactivation_date__for__employee_contract_id(
    employee_contract_id, deactivation_date
) -> EmployeeContract:
    employee_contract = EmployeeContract.objects.get(id=employee_contract_id)
    employee_contract.deactivation_date = deactivation_date
    employee_contract.save()
    return employee_contract


# Sets an employee contract as inactive for the given employee contract id
def set_employee_contract__as_inactive__for__employee_contract_id(
    employee_contract_id,
) -> EmployeeContract:

    # Gets the contract for the given employee contract id
    employee_contract = EmployeeContract.objects.get(id=employee_contract_id)

    # Sets the contract as inactive
    employee_contract.is_active = False

    # Sets the deactivation date to the current date
    employee_contract.deactivation_date = timezone.now()
    employee_contract.save()
    return employee_contract


# Checks if an employee contract exists for the given user code
def check__employee__exists__for__user_code(user_code) -> bool:
    return Employee.objects.filter(user__user_code=user_code).exists()


# Creates and returns a new employee  for the given user code
def create__employee__for__user_code(user_code) -> Employee | None:

    if not check__employee__exists__for__user_code(user_code):
        # create new employee for the user_code
        user = User.objects.get(user_code=user_code)
        return Employee.objects.create(user=user)

    return None


def check__employee_contract__exists__for__employee__and__customer_id(
    employee, cutomer_id
) -> bool:
    return EmployeeContract.objects.filter(
        employee=employee, customer__id=cutomer_id
    ).exists()


def create__employee_contract__between__employee_and__customer_id(
    employee, customer_id
) -> EmployeeContract:
    return EmployeeContract.objects.create(
        employee=employee,
        customer=Customer.objects.get(id=customer_id),
    )


# Returns the employee for the given user code
def get__employee__for__user_code(user_code) -> Employee:

    employee = None

    if not check__employee__exists__for__user_code(user_code):

        # create new employee for the user_code
        employee = create__employee__for__user_code(user_code)

    if employee == None:
        # get the employee object for the user
        employee = Employee.objects.get(user__user_code=user_code)

    return employee


def check__employee_manager_contract__exists__for__employee_contract(
    employee_contract,
) -> bool:
    return EmployeeManagerContract.objects.filter(contract=employee_contract).exists()


def check__more_then_one_contract_between__user_code__and__customer_id(
    user_code, customer_id
) -> bool:
    return (
        EmployeeContract.objects.filter(
            employee__user__user_code=user_code, customer__id=customer_id
        ).count()
        > 1
    )


def get__employee_contract__for__employee__and__customer_id(
    employee, customer_id
) -> EmployeeContract:

    # Check if the employee has a contract with the customer
    if not check__employee_contract__exists__for__employee__and__customer_id(
        employee, customer_id
    ):
        return create__employee_contract__between__employee_and__customer_id(
            employee, customer_id
        )
    else:
        return EmployeeContract.objects.get(employee=employee, customer__id=customer_id)


def get__employee_manager_contract__for__employee_contract(
    employee_contract,
) -> EmployeeManagerContract:

    # Check if the employee has an employee manager contract with the customer
    if not check__employee_manager_contract__exists__for__employee_contract(
        employee_contract
    ):
        return EmployeeManagerContract.objects.create(contract=employee_contract)
    else:
        return EmployeeManagerContract.objects.get(contract=employee_contract)


def get__employee_manager_contract__for__user_code__and__customer_id(
    user_code, customer_id
) -> EmployeeManagerContract:

    employee = get__employee__for__user_code(user_code)
    employee_contract = get__employee_contract__for__employee__and__customer_id(
        employee, customer_id
    )

    return get__employee_manager_contract__for__employee_contract(employee_contract)


def check__employee_manager_contract__for__user__can_deactivate__employee_contracts(
    user,
) -> bool:
    return EmployeeManagerContract.objects.filter(
        contract__employee=user.employee,
        contract__is_active=True,
        can_delete_employee=True,
    ).exists()


def check__employee_manager_contract__for__user__can_give_manager_role(
    user,
) -> bool:
    return EmployeeManagerContract.objects.filter(
        contract__employee=user.employee,
        contract__is_active=True,
        can_give_manager_role=True,
    ).exists()


def check__customer__exists__for__customer_id(customer_id) -> bool:
    return Customer.objects.filter(id=customer_id).exists()


def get__employee_contract__for__user_code__and__customer_id(
    user_code, customer_id
) -> EmployeeContract:

    employee = get__employee__for__user_code(user_code)
    employee_contract = get__employee_contract__for__employee__and__customer_id(
        employee, customer_id
    )

    return employee_contract


def get__customers__and__employees__for__employee_manager_contract__that_can_add_employees__for__user(
    user,
) -> list[dict[str, Union[Customer, Employee]]]:

    customers__and__employees__for__employee_manager_contract__that_can_add_employees__for__user = (
        []
    )

    # get all the customers the employee has contracts with and is an employee manager for
    # Do not use employee.employeemanager.list_of_customers_the_manager_is_responsible_for.all()!
    # Instead look at the contracts the employee has and get the customers from the contracts
    # This is because the employee manager will be deprecated in the future
    # Only list a customer once
    list_of_customers_the_employee_has_an_employee_manager_contract_with = get__list_of_customers__for__employee_manager_contract__that_can_add_employees__for__user(
        user
    )

    # get all the employees of the customers the user is responsible for
    for (
        customer
    ) in list_of_customers_the_employee_has_an_employee_manager_contract_with:

        if user.is_staff:
            customers__and__employees__for__employee_manager_contract__that_can_add_employees__for__user.append(
                [
                    customer,
                    EmployeeContract.objects.filter(customer=customer)
                    .distinct()
                    .order_by("-is_active"),
                    # user_can_deactivate_contracts
                    EmployeeManagerContract.objects.filter(
                        contract__employee=user.employee,
                        can_delete_employee=True,
                        contract__is_active=True,
                    ).exists(),
                ]
            )
        else:
            customers__and__employees__for__employee_manager_contract__that_can_add_employees__for__user.append(
                [
                    customer,
                    EmployeeContract.objects.filter(
                        customer=customer,
                        employee__user__is_staff=False,
                    )
                    .distinct()
                    .order_by("-is_active"),
                    # user_can_deactivate_contracts
                    EmployeeManagerContract.objects.filter(
                        contract__employee=user.employee,
                        can_delete_employee=True,
                        contract__is_active=True,
                    ).exists(),
                ]
            )

    return customers__and__employees__for__employee_manager_contract__that_can_add_employees__for__user


def get__list_of_customers__for__employee_manager_contract__that_can_add_employees__for__user(
    user,
) -> List[Customer]:

    list_of_employee_manager_contract_for_logged_in_user = (
        EmployeeManagerContract.objects.filter(
            contract__employee=user.employee, can_add_new_employee=True
        ).distinct("contract__customer")
    )

    # get the list of customers the employee manager is responsible for using the list_of_employee_manager_contract_for_logged_in_user
    return get__list_of_customers__for__list_of_employee_manager_contracts(
        list_of_employee_manager_contract_for_logged_in_user
    )


def get__list_of_customers__for__employee_manager_contract__that_can_give_the_role__for__user(
    user,
) -> List[Customer]:

    list_of_employee_manager_contract_for_logged_in_user = (
        EmployeeManagerContract.objects.filter(
            contract__employee=user.employee, can_give_manager_role=True
        ).distinct("contract__customer")
    )

    # get the list of customers the employee manager is responsible for using the list_of_employee_manager_contract_for_logged_in_user
    return get__list_of_customers__for__list_of_employee_manager_contracts(
        list_of_employee_manager_contract_for_logged_in_user
    )


def get__list_of_customers__for__list_of_employee_manager_contracts(
    list_of_employee_manager_contracts,
) -> List[Customer]:

    # get the list of customers the employee manager is responsible for using the list_of_employee_manager_contract_for_logged_in_user
    list_of_customers__for__employee_manager_contract = []
    for contract in list_of_employee_manager_contracts:
        list_of_customers__for__employee_manager_contract.append(
            contract.contract.customer
        )

    return list_of_customers__for__employee_manager_contract


# TODO add tests for this function and if it works correctly replace the part of the other fuctions that are looking for employee manager contracts
def get__list_of_employee_manager_contract__with__given_abitly__for__user(
    user, ability
) -> List[EmployeeManagerContract]:

    return EmployeeManagerContract.objects.filter(
        contract__employee=user.employee, **{ability: True}
    ).distinct("contract__customer")


def check__employee_manager_contract__exists__for__employee_manager_and_customer__and__can_add_users__and__is_active(
    employee_manager, customer
) -> bool:
    return EmployeeManagerContract.objects.filter(
        contract__employee=employee_manager,
        contract__customer=customer,
        contract__is_active=True,
        can_add_new_employee=True,
    ).exists()


def get__employee__for__user(user) -> Employee:
    return Employee.objects.get(user=user)


def get__price_per_hour__for__total_time_saved(total_time_saved: Decimal) -> Decimal:
    # print("total_time_saved", total_time_saved)

    price_per_hour = 0
    points = get__price_list()
    for time in points:
        if total_time_saved >= time:
            # If the time saved is greater than the time of the next point, the price of the last point before will be used
            price_per_hour = points[time]
        else:
            break

    return Decimal(price_per_hour)


def get__price_list() -> dict:
    # Define	points for the graph
    # The time saved starts at 0 seconds and increases with each point
    # The price starts at 230 and decreases with each point untill it reaches 30
    return {  # time: price
        0: 230,
        1: 230,
        2: 230,
        3: 230,
        4: 230,
        5: 230,
        6: 200,
        7: 200,
        8: 200,
        9: 200,
        10: 200,
        11: 170,
        12: 170,
        13: 170,
        14: 170,
        15: 170,
        16: 140,
        17: 140,
        18: 140,
        19: 140,
        20: 140,
        21: 110,
        22: 110,
        23: 110,
        24: 110,
        25: 110,
        26: 80,
        27: 80,
        28: 80,
        29: 80,
        30: 80,
        31: 50,
        32: 50,
        33: 50,
        34: 50,
        35: 50,
        36: 50,
        37: 50,
        38: 50,
        39: 50,
        40: 50,
        41: 50,
        42: 50,
        43: 50,
        44: 50,
        45: 30,
    }


# This function describes the logic for the price of executions
# It defines a graph that is used to calculate the price of executions
# To define the graph, a dictionare of points is used. Each point defines a price for a certain amount of time (in seconds) saved by the program
# The graph is defined by the points in the dictionary. With each exectution, the program will check if the time saved is greater than the time of the next point.
# Has the time saved exceeded the time of the next point, the price of the next point will be used. If the time saved is less than the time of the next point, the price of the current point will be used.
def get__new_price_per_second__for__customer_program(
    customer_program: CustomerProgram,
) -> Decimal:
    # print("Kommt bis hier hin")
    # Get the current amount of time saved by the program belonging to the customer program execution (in hours) check what the price should be
    # Get all the customer program executions belonging to the program of the customer program execution
    total_time_saved_program_executions_in_seconds = (
        get__total_time_saved__for__customer_program(customer_program)
    )

    """     print(
        "total_time_saved_program_executions_in_seconds",
        total_time_saved_program_executions_in_seconds,
    ) """

    total_time_saved_program_executions_in_hours = (
        total_time_saved_program_executions_in_seconds / 3600
    )

    # print(f"Total Time saved: {total_time_saved_program_executions_in_hours}")

    # Get the price for the current amount of time saved by the program belonging to the customer program execution
    price_per_hour = get__price_per_hour__for__total_time_saved(
        total_time_saved_program_executions_in_hours
    )

    print(f"Price per hour: {price_per_hour}")

    # TODO add things to calculate the price of the execution including discounts and stuff

    new_price_per_second = price_per_hour / 3600

    return new_price_per_second


def get__sum_of_time_saved_in_seconds__for__list_of_customer_program_exections(
    list_of_customer_program_executions,
) -> int:
    from django.db.models import Sum

    total_time_saved_in_seconds = list_of_customer_program_executions.aggregate(
        Sum("program_time_saved_in_seconds")
    )["program_time_saved_in_seconds__sum"]

    if total_time_saved_in_seconds == None:
        total_time_saved_in_seconds = 0

    return total_time_saved_in_seconds


def get__sum_of_price_for_execution__for__list_of_customer_program_exections(
    list_of_customer_program_executions,
) -> Decimal:
    from django.db.models import Sum

    # print("list_of_customer_program_executions", list_of_customer_program_executions)
    return list_of_customer_program_executions.aggregate(Sum("price_for_execution"))[
        "price_for_execution__sum"
    ]


# Returns the currently active TimeAccountManagerContracts for the user or None if there is no active one
def get__active_TimeAccountManagerContracts__for__employee(
    employee: Employee,
) -> QuerySet:

    # Get all the time account manager contracts of the user
    # This funcion retuns a QuerySet of all the TimeAccountManagerContracts of the user
    # The QuerySet is not evaluated until it is used
    # To now get the acive TimeAccountManagerContracts, apply the filter function to the QuerySet
    time_account_manager_contracts = get__TimeAccountMangerContracts__for__employee(
        employee
    )

    # Get all the active TimeAccountManagerContracts
    active_time_account_manager_contracts = time_account_manager_contracts.filter(
        contract__is_active=True,
    )

    return active_time_account_manager_contracts


def get__TimeAccountMangerContracts__for__employee(employee: Employee) -> QuerySet:

    # Get all the time account manager contracts of the user
    time_account_manager_contracts = TimeAccountManagerContract.objects.filter(
        contract__employee=employee,
    )

    return time_account_manager_contracts


def get__customer_time_accounts_grouped_by_customer_with_total_time_of_all_time_accounts__for__employee(
    employee: Employee,
) -> dict:
    # get all the customer time accounts the user has access to
    list_of_TimeAccountMangerContracts = (
        get__active_TimeAccountManagerContracts__for__employee(employee)
    )

    list_of_customer_time_accounts = (
        get__list_of_customer_time_accounts__for__list_of_TimeAccountMangerContracts(
            list_of_TimeAccountMangerContracts
        )
    )

    return get__customer_time_accounts_grouped_by_customer_with_total_time_of_all_time_accounts__for__list_of_customer_time_accounts(
        list_of_customer_time_accounts
    )

def set__all_active_NadooitApiKey__for__user_to_inactive(user: User) -> None:
    # Get all the active NadooitApiKey of the user
    list_of_active_NadooitApiKey = get__list_of_all_NadooitApiKey__for__user(user, is_active= True)

    # Set all the active NadooitApiKey to inactive
    for active_NadooitApiKey in list_of_active_NadooitApiKey:
        active_NadooitApiKey.is_active = False
        active_NadooitApiKey.save()	

def get__list_of_all_NadooitApiKey__for__user(user: User, is_active = True) -> QuerySet:
    return NadooitApiKey.objects.filter(user=user, is_active=is_active)


# Creates a new NADOO API key for the user and returns it. Optionally a uuid that is used as the api key can be passed
def create__NadooitApiKey__for__user(
    user: User, api_key_uuid: uuid = None
) -> NadooitApiKey:

    if api_key_uuid == None:
        api_key_uuid = uuid.uuid4()

    new_api_key = NadooitApiKey.objects.create(
        api_key=api_key_uuid,
        user=user,
        is_active=True,
    )
    new_api_key.updated_at = timezone.now()
    new_api_key.created_at = timezone.now()
    new_api_key.save()

    return new_api_key


def get__customer_time_accounts_grouped_by_customer_with_total_time_of_all_time_accounts__for__list_of_customer_time_accounts(
    list_of_customer_time_accounts: list,
) -> dict:

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

    print("customer_time_accounts_grouped_by_customer")
    print(customer_time_accounts_grouped_by_customer)

    return customer_time_accounts_grouped_by_customer


def get__list_of_customer_time_accounts__for__list_of_TimeAccountMangerContracts(
    list_of_TimeAccountMangerContracts: list,
) -> QuerySet:

    customers_the_user_works_for_as_timeaccountmanager = []
    for contract in list_of_TimeAccountMangerContracts:
        customers_the_user_works_for_as_timeaccountmanager.append(
            contract.contract.customer
        )

    list_of_customer_time_accounts = CustomerTimeAccount.objects.filter(
        customer__in=customers_the_user_works_for_as_timeaccountmanager
    )

    return list_of_customer_time_accounts


def set__customer_program__time_account__for__customer_program_execution(
    customer_program_execution: CustomerProgramExecution,
) -> None:
    # Get the time account of the customer program
    time_account = customer_program_execution.customer_program.time_account

    # Get the time saved by the program execution
    time_saved_in_seconds = customer_program_execution.program_time_saved_in_seconds

    # Reduce the time account by the time saved by the program execution
    reduce__time_account__by__time_in_seconds(time_account, time_saved_in_seconds)


def reduce__time_account__by__time_in_seconds(
    time_account: TimeAccount, time_in_seconds: int
) -> None:
    # First check if the time account has enough time to pay for the execution
    if time_account.time_balance_in_seconds >= time_in_seconds:
        # If the time account has enough time, the time saved by the execution will be subtracted from the time account
        time_account.time_balance_in_seconds -= time_in_seconds
    else:
        # If the time account does not have enough time, the time account will be set to 0
        time_account.time_balance_in_seconds = 0

    # Set the new time account
    time_account.save()


def get__price_for_new_customer_program_execution__for__cutomer_program(
    customer_program: CustomerProgram,
):

    print("get__price_for_new_customer_program_execution__for__cutomer_program")

    # The price for a program execution is calculated each time a new execution is added to the program
    # First it is checked if there is currently time allocated to the program already
    # If there is, the price for the exectution is 0 since the time is already paid for
    # If there is only partially enough time allocated to the program, the time not covered by the time allocated is calculated and the price for that time is calculated
    # If there is no time allocated to the program, the price for the execution is calculated based on the total time saved by all execution

    time_not_accounted_for_by_balance_on_time_accout_asociated_with_customer_program = 0

    # First it is checked if there is currently time allocated to the program already
    if (
        customer_program.time_account.time_balance_in_seconds
        - customer_program.program_time_saved_per_execution_in_seconds
        >= 0
    ):
        # If there is, the price for the exectution is 0 since the time is already paid for
        return 0
    elif (
        customer_program.time_account.time_balance_in_seconds
        - customer_program.program_time_saved_per_execution_in_seconds
        < 0
    ):
        print("customer_program.time_account", customer_program.time_account)

        # If there is only partially enough time allocated to the program, the time not covered by the time allocated is calculated and the price for that time is calculated
        # the time is alwasys positive
        time_not_accounted_for_by_balance_on_time_accout_asociated_with_customer_program = abs(
            customer_program.time_account.time_balance_in_seconds
            - customer_program.program_time_saved_per_execution_in_seconds
        )

        print(
            time_not_accounted_for_by_balance_on_time_accout_asociated_with_customer_program
        )

        return (
            get__new_price_per_second__for__customer_program(customer_program)
            * time_not_accounted_for_by_balance_on_time_accout_asociated_with_customer_program
        )


def create__customer_program_execution__for__customer_program(
    customer_program: CustomerProgram,
) -> CustomerProgramExecution:

    print("create__customer_program_execution__for__customer_program")

    # Create a new customer program execution with the current price for an execution
    customer_program_execution = CustomerProgramExecution.objects.create(
        customer_program=customer_program,
        program_time_saved_in_seconds=customer_program.program_time_saved_per_execution_in_seconds,
        price_for_execution=get__price_for_new_customer_program_execution__for__cutomer_program(
            customer_program
        ),
    )

    print("customer_program_execution", customer_program_execution)

    # Set the time account of the customer program execution
    set__customer_program__time_account__for__customer_program_execution(
        customer_program_execution
    )

    print("changed time account according to time of exectution")

    print("customer", customer_program.customer)

    set__new_price_per_second__for__customer_program(customer_program)

    return customer_program_execution


def set__new_price_per_second__for__customer_program(
    customer_program: CustomerProgram,
):
    customer_program.price_per_second = (
        get__new_price_per_second__for__customer_program(customer_program)
    )

    customer_program.save()


def get__next_customer_program_execution_price__for__customer_program_execution(
    customer_program_execution: CustomerProgramExecution,
):
    pass


def get__total_time_saved__for__customer_program(
    customer_program: CustomerProgram,
) -> Decimal:
    from django.db.models import Q

    return get__sum_of_time_saved_in_seconds__for__list_of_customer_program_exections(
        CustomerProgramExecution.objects.filter(
            Q(customer_program=customer_program) & Q(payment_status="PAID")
            | Q(payment_status="NOT_PAID")
        )
    )
    """ 
    return (
        CustomerProgramExecution.objects.filter(
            Q(customer_program=customer_program) & Q(payment_status="PAID")
            | Q(payment_status="NOT_PAID")
        )
    ).aggregate(Sum("program_time_saved_in_seconds"))[
        "program_time_saved_in_seconds__sum"
    ] """


def get__next_price_level__for__customer_program(
    customer_program: CustomerProgram,
) -> str:

    totat_time_saved = get__total_time_saved__for__customer_program(customer_program)

    # get the list of price levels
    list_of_price_levels = get__price_list()

    # get the price level for the total time saved
    currnet_price_level = get__price_per_hour__for__total_time_saved(totat_time_saved)

    # find the position in the list of price levels for the current price level and return the next price level
    for price_level in list_of_price_levels:
        if price_level == currnet_price_level:
            return list_of_price_levels[price_level + 1]
        else:
            continue


def get__nadooit_api_key__for__hashed_api_key(hashed_api_key) -> str:
    return NadooitApiKey.objects.get(api_key=hashed_api_key)


def get__hashed_api_key__for__request(request) -> str | None:
    """
    gets the hashed api key from the request
    """

    # gets the api key from the request
    api_key = request.data.get("NADOOIT__API_KEY")

    # hashes the api key
    hashed_api_key = hashlib.sha256(api_key.encode()).hexdigest()

    return hashed_api_key


def check__nadooit_api_key__has__is_active(hashed_api_key) -> bool:
    print("check__nadooit_api_key__has__is_active")
    return NadooitApiKey.objects.filter(api_key=hashed_api_key, is_active=True).exists()


def get__user_code__for__nadooit_api_key(nadooit_api_key) -> str:
    return nadooit_api_key.user.user_code
