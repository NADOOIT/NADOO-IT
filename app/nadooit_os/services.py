import math
from typing import List
import hashlib

from django.utils import timezone

from nadooit_program_ownership_system.models import CustomerProgram

from nadooit_api_key.models import NadooitApiKey
from nadooit_api_executions_system.models import CustomerProgramExecution
from nadooit_crm.models import Customer
from nadooit_hr.models import EmployeeManagerContract
from nadooit_hr.models import Employee
from nadooit_hr.models import EmployeeContract
from nadooit_auth.models import User
from datetime import datetime

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


def get__list_of_customers__for__employee_manager_contract__for_user(
    user,
) -> List[Customer]:

    list_of_employee_manager_contract_for_logged_in_user = (
        EmployeeManagerContract.objects.filter(
            contract__employee=user.employee, can_add_new_employee=True
        ).distinct("contract__customer")
    )

    # get the list of customers the employee manager is responsible for using the list_of_employee_manager_contract_for_logged_in_user
    list_of_customers__for__employee_manager_contract = []
    for contract in list_of_employee_manager_contract_for_logged_in_user:
        list_of_customers__for__employee_manager_contract.append(
            contract.contract.customer
        )

    return list_of_customers__for__employee_manager_contract


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


# This function describes the logic for the price of executions
# It defines a graph that is used to calculate the price of executions
# To define the graph, a dictionare of points is used. Each point defines a price for a certain amount of time (in seconds) saved by the program
# The graph is defined by the points in the dictionary. With each exectution, the program will check if the time saved is greater than the time of the next point.
# Has the time saved exceeded the time of the next point, the price of the next point will be used. If the time saved is less than the time of the next point, the price of the current point will be used.
def get__new_price_per_second_in_cent__for__customer_program(
    customer_program: CustomerProgram,
) -> float:
    from django.db.models import Q
    from django.db.models import Sum

    # Define	points for the graph
    # The time saved starts at 0 seconds and increases with each point
    # The price starts at 230 and decreases with each point untill it reaches 30
    points = {  # time: price
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
    print("Kommt bis hier hin")
    # Get the current amount of time saved by the program belonging to the customer program execution (in hours) check what the price should be
    # Get all the customer program executions belonging to the program of the customer program execution
    total_time_saved_program_executions_in_seconds = (
        CustomerProgramExecution.objects.filter(
            Q(customer_program=customer_program) & Q(payment_status="PAID")
            | Q(payment_status="NOT_PAID")
        )
    ).aggregate(Sum("program_time_saved_in_seconds"))

    print(total_time_saved_program_executions_in_seconds)
    print("Kommt bis hier hin 2")

    total_time_saved_program_executions_in_hours = (
        total_time_saved_program_executions_in_seconds[
            "program_time_saved_in_seconds__sum"
        ]
        / 3600
    )

    print(total_time_saved_program_executions_in_hours)

    # Get the price for the current amount of time saved by the program belonging to the customer program execution
    price_per_hour = 0
    for time in points:
        if total_time_saved_program_executions_in_hours > time:
            # If the time saved is greater than the time of the next point, the price of the last point before will be used
            price_per_hour = points[time]
        else:
            break

    print(price_per_hour)

    # TODO add things to calculate the price of the execution including discounts and stuff

    price_in_seconds = price_per_hour / 3600

    return price_in_seconds


def get__nadooit_api_key__for__hashed_api_key(hashed_api_key) -> str:
    return NadooitApiKey.objects.get(api_key=hashed_api_key)


def get__hashed_api_key__for__request(request) -> str:
    """
    gets the hashed api key from the request
    """
    # gets the api key from the request
    api_key = request.data.get("NADOOIT__API_KEY")

    # hashes the api key
    hashed_api_key = hashlib.sha256(api_key.encode()).hexdigest()

    return hashed_api_key


def check__nadooit_api_key__has__is_active(hashed_api_key) -> bool:
    return NadooitApiKey.objects.filter(api_key=hashed_api_key, is_active=True).exists()


def get__user_code__for__nadooit_api_key(nadooit_api_key) -> str:
    return nadooit_api_key.user.user_code
