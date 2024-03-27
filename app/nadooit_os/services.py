import csv
import decimal
import hashlib
import math
import re
import uuid
from datetime import datetime
from decimal import Decimal
from typing import List, Union

# import Q for filtering
from django.db.models import Q, QuerySet
from django.http import HttpResponse, HttpResponseRedirect
from django.utils import timezone
from nadoo_complaint_management.models import Complaint
from nadooit_api_executions_system.models import CustomerProgramExecution
from nadooit_api_key.models import NadooitApiKey
from nadooit_auth.models import User
from nadooit_crm.models import Customer
from nadooit_hr.models import (
    CustomerManagerContract,
    CustomerProgramExecutionManagerContract,
    CustomerProgramManagerContract,
    Employee,
    EmployeeContract,
    EmployeeManagerContract,
    TimeAccountManagerContract,
)
from nadooit_program_ownership_system.models import CustomerProgram
from nadooit_time_account.models import CustomerTimeAccount, TimeAccount

# logging
import logging

logger = logging.getLogger(__name__)


def get__not_paid_customer_program_executions__for__filter_type_and_customer(
    filter_type, customer
):
    customer_program_executions = (
        get__customer_program_executions__for__filter_type_and_customer(
            filter_type, customer
        ).filter(payment_status="NOT_PAID")
    )
    return customer_program_executions


def get__customer_program_executions__for__filter_type_and_customer(
    filter_type, customer
) -> QuerySet:
    from datetime import date

    todays_date = date.today()
    customer_program_executions = None
    if filter_type == "lastmonth":

        print(todays_date.month)
        print(todays_date.month - 1)

        if todays_date.month == 1:
            customer_program_executions = (
                CustomerProgramExecution.objects.filter(
                    customer_program__customer=customer,
                    created_at__month=12,
                    created_at__year=todays_date.year - 1,
                )
                .order_by("created_at")
                .reverse()
            )
        else:
            customer_program_executions = (
                CustomerProgramExecution.objects.filter(
                    customer_program__customer=customer,
                    created_at__month=todays_date.month - 1,
                )
                .order_by("created_at")
                .reverse()
            )
    elif filter_type == "today":
        customer_program_executions = (
            CustomerProgramExecution.objects.filter(
                customer_program__customer=customer, created_at__date=todays_date
            )
            .order_by("created_at")
            .reverse()
        )
    elif filter_type == "last20":
        customer_program_executions = (
            CustomerProgramExecution.objects.filter(customer_program__customer=customer)
            .order_by("created_at")
            .reverse()
        )
    elif filter_type == "thismonth":
        customer_program_executions = (
            CustomerProgramExecution.objects.filter(
                customer_program__customer=customer,
                created_at__month=todays_date.month,
                created_at__year=todays_date.year,
            )
            .order_by("created_at")
            .reverse()
        )
    elif filter_type == "thisyear":
        customer_program_executions = (
            CustomerProgramExecution.objects.filter(
                customer_program__customer=customer,
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

    # Also add a . so the format becomes 111.111,00 €

    price_as_string = re.sub(r"(\d)(?=(\d{3})+(?!\d))", r"\1.", price_as_string)

    return f"{price_as_string} €"


def get__time_as_string_in_hour_format__for__time_in_seconds_as_integer(time) -> str:
    # The format of the final string should result in something like this "25 std : 03 min : 05 sek"
    return f"{math.floor(time / 3600)} std : {math.floor((time % 3600) / 60)} min : {math.floor(time % 60)} sek"


# Refactore this function because it requeres an employee and not a user. This is dangerous because it is not clear by the name of the function
def check__user__is__customer_program_manager__for__customer_prgram(
    user: User, customer_program: CustomerProgram
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


def get__list_of_customers__for__employee_that_has_a_time_account_manager_contract_with_and_can_create_time_account_manager_contracts_for_them(
    employee,
):
    print("employee", employee)
    list_of_time_account_manager_contracts__for__employee__where__employee_is_time_account_manager_and_can_create_time_account_manager_contracts = get__list_of_time_account_manager_contracts__for__employee__where__employee_is_time_account_manager_and_can_create_time_account_manager_contracts(
        employee=employee
    )

    print(
        list_of_time_account_manager_contracts__for__employee__where__employee_is_time_account_manager_and_can_create_time_account_manager_contracts
    )

    # get the list of customers the customer program manager is responsible for using the list_of_customer_program_execution_manager_contract
    list_of_customers_the_manager_is_responsible_for = []
    for (
        contract
    ) in list_of_time_account_manager_contracts__for__employee__where__employee_is_time_account_manager_and_can_create_time_account_manager_contracts:
        list_of_customers_the_manager_is_responsible_for.append(
            contract.contract.customer
        )

    return list_of_customers_the_manager_is_responsible_for


def get__list_of_customers_the_employee_has_a_customer_programm_manager_contract_with_and_the_customer_programms__for__employee(
    employee: Employee,
):

    customers_the_user_is_responsible_for_and_the_customer_programms = []
    
    """ 
    list_of_customer_program_manger_contract_for_logged_in_user = (
        CustomerProgramManagerContract.objects.filter(
            contract__employee=employee, can_give_manager_role=True
        ).distinct("contract__customer")
    )
    """
    
    list_of_customer_program_manger_contract_for_logged_in_user = (
        CustomerProgramManagerContract.objects.filter(
            contract__employee=employee,
            can_give_manager_role=True,
            contract__customer__in=CustomerProgramManagerContract.objects.filter(
                contract__employee=employee,
                can_give_manager_role=True
            ).values_list('contract__customer', flat=True).distinct()
        )
    )


    # get the list of customers the customer program manager is responsible for using the list_of_customer_program_manger_contract_for_logged_in_user
    for contract in list_of_customer_program_manger_contract_for_logged_in_user:

        # list of customer programms with of the customer
        customer_programms = CustomerProgram.objects.filter(
            customer=contract.contract.customer
        )

        # add the customer and the customer programm execution to the list
        customers_the_user_is_responsible_for_and_the_customer_programms.append(
            [contract.contract.customer, list(customer_programms)]
        )

    return customers_the_user_is_responsible_for_and_the_customer_programms


def check__active_customer_program_execution_manager_contract__exists__between__employee_and_customer(
    employee: Employee, customer: Customer
):
    return CustomerProgramExecutionManagerContract.objects.filter(
        contract__employee=employee,
        contract__is_active=True,
        contract__customer=customer,
    ).exists()


def get__list_of_time_account_manager_contracts__for__employee__where__employee_is_time_account_manager_and_can_create_time_account_manager_contracts(
    employee,
):
    
    """     
    return TimeAccountManagerContract.objects.filter(
        contract__employee=employee, can_give_manager_role=True
    ).distinct("contract__customer")
    """

    return TimeAccountManagerContract.objects.filter(
        contract__employee=employee,
        can_give_manager_role=True,
        contract__customer__in=TimeAccountManagerContract.objects.filter(
            contract__employee=employee,
            can_give_manager_role=True
        ).values_list('contract__customer', flat=True).distinct()
    )

def create__time_account_manager_contract__for__user_code_customer_and_list_of_abilities_according_to_employee_creating_contract(
    user_code, customer, list_of_abilities, employee_creating_contract
) -> TimeAccountManagerContract | None:

    # check if there is an emplyee for that user code
    if not check__employee__exists__for__user_code(user_code):
        # create new employee for the user_code
        create__employee__for__user_code(user_code)

    # get the employee object for the user
    employee = get__employee__for__user_code(user_code)

    # check if the employee already has the role for the customer
    if not check__time_account_manager_contract__exists__for__employee_and_customer(
        employee, customer
    ):
        # Check if the employee has a contract with the customer

        if not check__employee_contract__exists__for__employee__and__customer(
            employee, customer
        ):
            create__employee_contract__for__employee_and__customer(employee, customer)
        # create the CustomerProgramExecutionManager
        TimeAccountManagerContract.objects.create(
            contract=EmployeeContract.objects.get(employee=employee)
        )
    # give the employee the roles that were selected and are stored in selected_abilities, the possible abilities are stored in the list of abilities
    # get the "role"
    # TODO: #115 refactor so that the list of abilites is retrieved from the model and not hardcoded
    for ability in list_of_abilities:
        # check if the employee already has the ability
        if ability == "can_create_time_accounts":
            if TimeAccountManagerContract.objects.filter(
                contract__employee=employee_creating_contract,
                contract__customer=customer,
                can_create_time_accounts=True,
            ).exists():
                # Set the ability for the TimeAccountManagerContract object to the value of the ability
                TimeAccountManagerContract.objects.filter(
                    contract__employee=employee,
                    contract__customer=customer,
                ).update(can_create_time_accounts=True)
        if ability == "can_delete_time_accounts":
            if TimeAccountManagerContract.objects.filter(
                contract__employee=employee_creating_contract,
                contract__customer=customer,
                can_delete_time_accounts=True,
            ).exists():
                # Set the ability for the TimeAccountManagerContract object to the value of the ability
                TimeAccountManagerContract.objects.filter(
                    contract__employee=employee,
                    contract__customer=customer,
                ).update(can_delete_time_accounts=True)
        if ability == "can_give_manager_role":
            if TimeAccountManagerContract.objects.filter(
                contract__employee=employee_creating_contract,
                contract__customer=customer,
                can_give_manager_role=True,
            ).exists():
                # Set the ability for the CustomerProgramExecutionManager object to the value of the ability
                TimeAccountManagerContract.objects.filter(
                    contract__employee=employee,
                    contract__customer=customer,
                ).update(can_give_manager_role=True)
    return TimeAccountManagerContract.objects.get(
        contract__employee=employee, contract__customer=customer
    )


def create__employee_manager_contract__for__user_code_customer_and_list_of_abilities_according_to_employee_creating_contract(
    user_code,
    customer: Customer,
    list_of_abilities,
    employee_creating_contract: Employee,
) -> EmployeeManagerContract | None:

    # check if there is an emplyee for that user code
    if not check__employee__exists__for__user_code(user_code):
        # create new employee for the user_code
        create__employee__for__user_code(user_code)

    # get the employee object for the user
    employee = get__employee__for__user_code(user_code)

    # check if the employee already has the role for the customer
    if not check__time_account_manager_contract__exists__for__employee_and_customer(
        employee, customer
    ):
        # Check if the employee has a contract with the customer

        if not check__employee_contract__exists__for__employee__and__customer(
            employee, customer
        ):
            create__employee_contract__for__employee_and__customer(employee, customer)
        # create the CustomerProgramExecutionManager
        EmployeeManagerContract.objects.create(
            contract=EmployeeContract.objects.get(employee=employee)
        )
    # give the employee the roles that were selected and are stored in selected_abilities, the possible abilities are stored in the list of abilities
    # get the "role"
    # TODO: #116 refactor so that the list of abilites is retrieved from the model and not hardcoded
    for ability in list_of_abilities:
        # check if the employee already has the ability
        if ability == "can_add_new_employee":
            if EmployeeManagerContract.objects.filter(
                contract__employee=employee_creating_contract,
                contract__customer=customer,
                can_add_new_employee=True,
            ).exists():
                # Set the ability for the TimeAccountManagerContract object to the value of the ability
                EmployeeManagerContract.objects.filter(
                    contract__employee=employee,
                    contract__customer=customer,
                ).update(can_add_new_employee=True)
        if ability == "can_delete_employee":
            if EmployeeManagerContract.objects.filter(
                contract__employee=employee_creating_contract,
                contract__customer=customer,
                can_delete_employee=True,
            ).exists():
                # Set the ability for the TimeAccountManagerContract object to the value of the ability
                EmployeeManagerContract.objects.filter(
                    contract__employee=employee,
                    contract__customer=customer,
                ).update(can_delete_employee=True)
        if ability == "can_give_manager_role":
            if EmployeeManagerContract.objects.filter(
                contract__employee=employee_creating_contract,
                contract__customer=customer,
                can_give_manager_role=True,
            ).exists():
                # Set the ability for the CustomerProgramExecutionManager object to the value of the ability
                EmployeeManagerContract.objects.filter(
                    contract__employee=employee,
                    contract__customer=customer,
                ).update(can_give_manager_role=True)
    return EmployeeManagerContract.objects.get(
        contract__employee=employee, contract__customer=customer
    )


def get__list_of_customer_program_execution_manager_contracts__for__employee__where__employee_is_customer_program_execution_manager(
    employee: Employee, contract_state="active"
):
    
    """ 
    if contract_state == "active":
        return CustomerProgramExecutionManagerContract.objects.filter(
            contract__employee=employee, contract__is_active=True
        ).distinct("contract__customer")
    elif contract_state == "inactive":
        return CustomerProgramExecutionManagerContract.objects.filter(
            contract__employee=employee, contract__is_active=False
        ).distinct("contract__customer")
    elif contract_state == "all":
        return CustomerProgramExecutionManagerContract.objects.filter(
            contract__employee=employee
        ).distinct("contract__customer")
    """
    
    if contract_state == "active":
        return CustomerProgramExecutionManagerContract.objects.filter(
            contract__employee=employee,
            contract__is_active=True,
            contract__customer__in=CustomerProgramExecutionManagerContract.objects.filter(
                contract__employee=employee,
                contract__is_active=True
            ).values_list('contract__customer', flat=True).distinct()
        )
    elif contract_state == "inactive":
        return CustomerProgramExecutionManagerContract.objects.filter(
            contract__employee=employee,
            contract__is_active=False,
            contract__customer__in=CustomerProgramExecutionManagerContract.objects.filter(
                contract__employee=employee,
                contract__is_active=False
            ).values_list('contract__customer', flat=True).distinct()
        )
    elif contract_state == "all":
        return CustomerProgramExecutionManagerContract.objects.filter(
            contract__employee=employee,
            contract__customer__in=CustomerProgramExecutionManagerContract.objects.filter(
                contract__employee=employee
            ).values_list('contract__customer', flat=True).distinct()
        )

def get__list_of_customer_program_manger_contracts__for__employee__where__employee_is_customer_program_manager(
    employee: Employee, contract_state="active"
):
    """ 
    if contract_state == "active":
        return CustomerProgramManagerContract.objects.filter(
            contract__employee=employee, contract__is_active=True
        ).distinct("contract__customer")
    elif contract_state == "inactive":
        return CustomerProgramManagerContract.objects.filter(
            contract__employee=employee, contract__is_active=False
        ).distinct("contract__customer")
    elif contract_state == "all":
        return CustomerProgramManagerContract.objects.filter(
            contract__employee=employee
        ).distinct("contract__customer")
    """
     
    if contract_state == "active":
        return CustomerProgramManagerContract.objects.filter(
            contract__employee=employee,
            contract__is_active=True,
            contract__customer__in=CustomerProgramManagerContract.objects.filter(
                contract__employee=employee,
                contract__is_active=True
            ).values_list('contract__customer', flat=True).distinct()
        )
    elif contract_state == "inactive":
        return CustomerProgramManagerContract.objects.filter(
            contract__employee=employee,
            contract__is_active=False,
            contract__customer__in=CustomerProgramManagerContract.objects.filter(
                contract__employee=employee,
                contract__is_active=False
            ).values_list('contract__customer', flat=True).distinct()
        )
    elif contract_state == "all":
        return CustomerProgramManagerContract.objects.filter(
            contract__employee=employee,
            contract__customer__in=CustomerProgramManagerContract.objects.filter(
                contract__employee=employee
            ).values_list('contract__customer', flat=True).distinct()
        )


def get__list_of_customer_program_execution__for__employee_and_filter_type__grouped_by_customer(
    employee: Employee, filter_type: str = "last20"
) -> list:

    print("employee", employee)
    print("filter_type", filter_type)

    list_of_customer_program_execution__for__employee_and_filter_type__grouped_by_customer = (
        []
    )

    list_of_customer_program_execution_manager_contracts__for__employee = get__list_of_customer_program_execution_manager_contracts__for__employee__where__employee_is_customer_program_execution_manager(
        employee
    )
    print(
        "list_of_customer_program_manger_contract_for_logged_in_user",
        list_of_customer_program_execution_manager_contracts__for__employee,
    )

    # Get the executions depending on the filter type
    customer_program_executions = []

    # get the list of customers the customer program manager is responsible for using the list_of_customer_program_execution_manager_contracts__for__employee
    for contract in list_of_customer_program_execution_manager_contracts__for__employee:

        # list of customer programms with of the customer
        """
        customer_program_executions = (
            CustomerProgramExecution.objects.filter(
                customer_program__customer=contract.contract.customer
            )
            .order_by("created_at")
            .reverse()[:20]
        )
        """

        if filter_type == "last20":

            customer_program_executions = (
                get__customer_program_executions__for__filter_type_and_customer(
                    filter_type, contract.contract.customer
                )[:20]
            )

        else:
            customer_program_executions = (
                get__customer_program_executions__for__filter_type_and_customer(
                    filter_type, contract.contract.customer
                )
            )

        # add the customer and the customer programm execution to the list
        list_of_customer_program_execution__for__employee_and_filter_type__grouped_by_customer.append(
            [contract.contract.customer, customer_program_executions]
        )

    return list_of_customer_program_execution__for__employee_and_filter_type__grouped_by_customer


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
        if not check__user__exists__for__user_code(user_code):
            return None
        user = User.objects.get(user_code=user_code)
        return Employee.objects.create(user=user)

    return Employee.objects.get(user__user_code=user_code)


def check__employee_contract__exists__for__employee__and__customer(
    employee: Employee, cutomer: Customer
) -> bool:
    return EmployeeContract.objects.filter(employee=employee, customer=cutomer).exists()


def get__employee_contract__for__employee_and_customer(
    employee: Employee, customer: Customer
) -> EmployeeContract | None:
    # Check if the employee contract exists
    if not check__employee_contract__exists__for__employee__and__customer(
        employee, customer
    ):
        return create__employee_contract__for__employee_and__customer(
            employee, customer
        )

    return EmployeeContract.objects.get(employee=employee, customer=customer)


def create__employee_contract__for__employee_and__customer(
    employee, customer
) -> EmployeeContract:
    return EmployeeContract.objects.create(
        employee=employee,
        customer=customer,
    )


# Returns the customer for the given customer id, the check if the customer exists is not done here and should be done before
def get__customer__for__customer_id(customer_id) -> Customer | None:

    try:
        return Customer.objects.get(id=customer_id)
    except:
        return None


# checks if a TimeAccountManagerContract exists for the given employee
def check__time_account_manager_contract__exists__for__employee_and_customer(
    employee, customer
) -> bool:
    return TimeAccountManagerContract.objects.filter(
        contract__employee=employee, contract__customer=customer
    ).exists()


def get__list_of_customer_program_execution_manager_contract__for__employee(
    employee: Employee,
) -> List[CustomerProgramExecutionManagerContract]:

    """ 
    return CustomerProgramExecutionManagerContract.objects.filter(
        contract__employee=employee,
        can_give_manager_role=True,
    ).distinct("contract__customer")
    """

    return CustomerProgramExecutionManagerContract.objects.filter(
        contract__employee=employee,
        can_give_manager_role=True,
        contract__customer__in=CustomerProgramExecutionManagerContract.objects.filter(
            contract__employee=employee,
            can_give_manager_role=True
        ).values_list('contract__customer', flat=True).distinct()
    )


def get__customer_program_manager_contract__for__employee_and_customer(
    employee: Employee, customer: Customer
) -> CustomerProgramManagerContract:

    # check if there is a customer program manager contract for the given employee and customer
    # if there is no contract create one
    if not check__customer_program_manager_contract__exists__for__employee_and_customer(
        employee=employee, customer=customer
    ):
        return create__customer_program_manager_contract__for__employee_and__customer(
            employee=employee, customer=customer
        )

    return CustomerProgramManagerContract.objects.get(
        contract__employee=employee,
        contract__customer=customer,
    )


# the list of abilities is a list of strings
# the strings are the names of the abilities that the customer program manager contract has
# meaning that the abilites in the customer program manager contract are the ones that are set to true
def get__list_of_abilties__for__customer_program_manager_contract(
    customer_program_manager_contract: CustomerProgramManagerContract,
) -> List[str]:

    # get the abilities of the customer program manager contract
    # the returned abilities are a dictionary with the ability names as keys and the ability values as values
    abilities = customer_program_manager_contract.get_abilities()

    # create a list of the ability names that are set to true

    list_of_abilities = []
    for ability in abilities:
        if abilities[ability]:
            list_of_abilities.append(ability)

    return list_of_abilities


def get__list_of_abilities__for__list_of_selected_abilities_and_list_of_possible_abilities_the_employee_can_give(
    list_of_selected_abilities: List[str], list_of_possible_abilities: List[str]
) -> List[str]:

    # create a list of the abilities that the employee can give
    # the abilities that the employee can give are the ones that are in the selected abilities
    # and the ones that are in the possible abilities
    list_of_abilities = []
    for ability in list_of_selected_abilities:
        if ability in list_of_possible_abilities:
            list_of_abilities.append(ability)

    return list_of_abilities


def set__list_of_abilities__for__customer_program_manager_contract_according_to_list_of_abilities(
    customer_program_manager_contract: CustomerProgramManagerContract,
    list_of_abilities: List[str],
) -> None:
    for ability in list_of_abilities:
        # check if the employee already has the ability
        if ability == "can_create_customer_program":
            # Set the ability for the CustomerProgramManagerContract object to the value of the ability
            customer_program_manager_contract.can_create_customer_program = True
        if ability == "can_delete_customer_program":
            customer_program_manager_contract.can_delete_customer_program = True
        if ability == "can_give_manager_role":
            customer_program_manager_contract.can_give_manager_role = True

    # save the changes to the database
    customer_program_manager_contract.save()


def create__customer_program_manager_contract__for__employee_and__customer(
    employee: Employee, customer: Customer
) -> CustomerProgramManagerContract:

    # create a new employee contract for the given employee and customer
    employee_contract = get__employee_contract__for__employee_and_customer(
        employee=employee, customer=customer
    )

    # create a new customer program manager contract for the given employee contract
    return CustomerProgramManagerContract.objects.create(contract=employee_contract)


def check__customer_program_manager_contract__exists__for__employee_and_customer(
    employee: Employee, customer: Customer
) -> bool:

    return CustomerProgramManagerContract.objects.filter(
        contract__employee=employee, contract__customer=customer
    ).exists()


def get__list_of_customers_the_employee_has_a_customer_program_execution_manager_contract_with_and_can_create_such_a_contract(
    employee: Employee,
) -> List[Customer]:

    # get the list of customers the customer program manager is responsible for
    list_of_customer_program_execution_manager_contract = (
        get__list_of_customer_program_execution_manager_contract__for__employee(
            employee=employee
        )
    )

    # get the list of customers the customer program manager is responsible for using the list_of_customer_program_execution_manager_contract
    list_of_customers_the_manager_is_responsible_for = []
    for contract in list_of_customer_program_execution_manager_contract:
        list_of_customers_the_manager_is_responsible_for.append(
            contract.contract.customer
        )

    return list_of_customers_the_manager_is_responsible_for


def create__customer_program_execution_manager_contract__for__employee_and_customer_and_list_of_abilities_and_employee_with_customer_program_manager_contract(
    employee,
    customer,
    list_of_abilities,
    employee_with_customer_program_manager_contract,
) -> CustomerProgramExecutionManagerContract:

    # check if the employee already has the role and if not create it
    if not check__active_customer_program_execution_manager_contract__exists__between__employee_and_customer(
        employee, customer
    ):

        # TODO what if there is an old inactive contract?
        # no new contract should be created if there is an old inactive contract and instead the old contract should be activated
        # better yet the person that is trying to create a new contract should be notified that there is an old inactive contract and that the old contract should be activated instead of creating a new contract

        # Check if the employee has a contract with the customer
        employee_contract = get__active_employee_contract__for__employee__and__customer(
            employee, customer
        )

        create__customer_program_execution_manager_contract__for__employee_contract(
            employee_contract=employee_contract
        )

    # give the employee the roles that were selected and are stored in selected_abilities, the possible abilities are stored in the list of abilities
    for ability in list_of_abilities:
        # check if the employee already has the ability
        if ability == "can_create_customer_program_execution":
            if CustomerProgramExecutionManagerContract.objects.filter(
                contract__employee=employee_with_customer_program_manager_contract,
                can_create_customer_program_execution=True,
            ).exists():
                # Set the ability for the CustomerProgramExecutionManagerContract object to the value of the ability
                CustomerProgramExecutionManagerContract.objects.filter(
                    contract__employee=employee
                ).update(can_create_customer_program_execution=True)
        if ability == "can_delete_customer_program_execution":
            if CustomerProgramExecutionManagerContract.objects.filter(
                contract__employee=employee_with_customer_program_manager_contract,
                can_delete_customer_program_execution=True,
            ).exists():
                # Set the ability for the CustomerProgramExecutionManagerContract object to the value of the ability
                CustomerProgramExecutionManagerContract.objects.filter(
                    contract__employee=employee
                ).update(can_delete_customer_program_execution=True)
        if ability == "can_give_manager_role":
            if CustomerProgramExecutionManagerContract.objects.filter(
                contract__employee=employee_with_customer_program_manager_contract,
                can_give_manager_role=True,
            ).exists():
                # Set the ability for the CustomerProgramExecutionManager object to the value of the ability
                CustomerProgramExecutionManagerContract.objects.filter(
                    contract__employee=employee
                ).update(can_give_manager_role=True)

    return CustomerProgramExecutionManagerContract.objects.get(
        contract__employee=employee, contract__customer=customer
    )


# Returns the employee for the given user code
def get__employee__for__user_code(user_code) -> Employee | None:

    employee = None

    if not check__employee__exists__for__user_code(user_code):

        # create new employee for the user_code
        employee = create__employee__for__user_code(user_code)

    if employee == None:
        # get the employee object for the user
        employee = Employee.objects.filter(user__user_code=user_code).first()

    return employee


def check__employee_manager_contract__exists__for__employee_contract(
    employee_contract,
) -> bool:
    return EmployeeManagerContract.objects.filter(contract=employee_contract).exists()


def check__more_then_one_contract_between__user_code__and__customer(
    user_code, customer_id
) -> bool:
    return (
        list(
            EmployeeContract.objects.filter(
                employee__user__user_code=user_code, customer__id=customer_id
            )
        ).count()
        > 1
    )


def create__customer_program_execution_manager_contract__for__employee_contract(
    employee_contract: EmployeeContract,
) -> CustomerProgramExecutionManagerContract:

    # Check if the employee contract is already a customer program execution manager contract
    if check__customer_program_execution_manager_contract__exists__for__employee_contract(
        employee_contract
    ):
        return CustomerProgramExecutionManagerContract.objects.get(
            contract=employee_contract
        )

    return CustomerProgramExecutionManagerContract.objects.create(
        contract=employee_contract
    )


def check__customer_program_execution_manager_contract__exists__for__employee_contract(
    employee_contract: EmployeeContract,
) -> bool:
    return CustomerProgramExecutionManagerContract.objects.filter(
        contract=employee_contract
    ).exists()


def get__active_employee_contract__for__employee__and__customer(
    employee: Employee, customer: Customer
) -> EmployeeContract:

    # Check if the employee has a contract with the customer
    if not check__employee_contract__exists__for__employee__and__customer(
        employee, customer
    ):
        return create__employee_contract__for__employee_and__customer(
            employee, customer
        )
    else:
        # Check if the employee has an active contract with the customer and return it
        employee_contract = EmployeeContract.objects.filter(
            employee=employee, customer=customer
        ).first()

        if not employee_contract.is_active:
            # activate the contract
            employee_contract.is_active = True
            employee_contract.save()

        return employee_contract


def get__employee_contract__for__employee__and__customer(
    employee: Employee, customer: Customer
) -> EmployeeContract:

    # Check if the employee has a contract with the customer
    if not check__employee_contract__exists__for__employee__and__customer(
        employee, customer
    ):
        return create__employee_contract__for__employee_and__customer(
            employee, customer
        )
    else:
        return EmployeeContract.objects.get(employee=employee, customer=customer)


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


def get__employee_manager_contract__for__user_code__and__customer(
    user_code, customer_id
) -> EmployeeManagerContract:

    employee = get__employee__for__user_code(user_code)
    employee_contract = get__employee_contract__for__employee__and__customer(
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


def get__employee_contract__for__user_code__and__customer(
    user_code, customer
) -> EmployeeContract:

    employee = get__employee__for__user_code(user_code)
    employee_contract = get__employee_contract__for__employee__and__customer(
        employee, customer
    )

    return employee_contract


def get__list_of_customers__and__their_employees__for__customers_that_have_a_employee_manager_contract__for__user(
    user,
):

    customers__and__employees__for__employee_manager_contract__for__user = []

    # get all the customers the employee has contracts with and is an employee manager for
    # Do not use employee.employeemanager.list_of_customers_the_manager_is_responsible_for.all()!
    # Instead look at the contracts the employee has and get the customers from the contracts
    # This is because the employee manager will be deprecated in the future
    # Only list a customer once
    list_of_customers_the_employee_has_an_employee_manager_contract_with = (
        get__list_of_customers__for__employee_manager_contract__for__user(user)
    )

    # get all the employees of the customers the user is responsible for
    for (
        customer
    ) in list_of_customers_the_employee_has_an_employee_manager_contract_with:

        if user.is_staff:
            customers__and__employees__for__employee_manager_contract__for__user.append(
                [
                    customer,
                    list(
                        EmployeeContract.objects.filter(customer=customer)
                        .distinct()
                        .order_by("-is_active"),
                        # user_can_deactivate_contracts
                    ),
                    EmployeeManagerContract.objects.filter(
                        contract__employee=user.employee,
                        can_delete_employee=True,
                        contract__is_active=True,
                    ).exists(),
                ]
            )
        else:
            customers__and__employees__for__employee_manager_contract__for__user.append(
                [
                    customer,
                    list(
                        EmployeeContract.objects.filter(
                            customer=customer,
                            employee__user__is_staff=False,
                        )
                        .distinct()
                        .order_by("-is_active")
                    ),
                    # user_can_deactivate_contracts
                    EmployeeManagerContract.objects.filter(
                        contract__employee=user.employee,
                        can_delete_employee=True,
                        contract__is_active=True,
                    ).exists(),
                ]
            )

    return customers__and__employees__for__employee_manager_contract__for__user


def get__list_of_employee_manager_contracts_that_can_add_new_employees__for__user(
    user,
) -> List[EmployeeManagerContract]:
    
    """ 
    return EmployeeManagerContract.objects.filter(
        contract__employee=user.employee, can_add_new_employee=True
    ).distinct("contract__customer")
    """
    
    return EmployeeManagerContract.objects.filter(
        contract__employee=user.employee,
        can_add_new_employee=True,
        contract__customer__in=EmployeeManagerContract.objects.filter(
            contract__employee=user.employee,
            can_add_new_employee=True
        ).values_list('contract__customer', flat=True).distinct()
    )


def get__list_of_employee_manager_contracts__for__user(
    user,
) -> List[EmployeeManagerContract]:
    
    """     
    return EmployeeManagerContract.objects.filter(
        contract__employee=user.employee,
    ).distinct("contract__customer")
    """
    
    return EmployeeManagerContract.objects.filter(
        contract__employee=user.employee,
        contract__customer__in=EmployeeManagerContract.objects.filter(
            contract__employee=user.employee
        ).values_list('contract__customer', flat=True).distinct()
    )


def get__list_of_customers__for__employee_manager_contract__that_can_add_employees__for__user(
    user,
) -> List[Customer]:

    list_of_employee_manager_contracts = (
        get__list_of_employee_manager_contracts_that_can_add_new_employees__for__user(
            user
        )
    )

    # get the list of customers the employee manager is responsible for using the list_of_employee_manager_contracts
    return get__list_of_customers__for__list_of_employee_manager_contracts(
        list_of_employee_manager_contracts
    )


def get__list_of_customers__for__employee_manager_contract__for__user(
    user,
) -> List[Customer]:

    list_of_employee_manager_contracts = (
        get__list_of_employee_manager_contracts__for__user(user)
    )

    # get the list of customers the employee manager is responsible for using the list_of_employee_manager_contracts
    return get__list_of_customers__for__list_of_employee_manager_contracts(
        list_of_employee_manager_contracts
    )


def get__list_of_customers__for__employee_manager_contract__that_can_give_the_role__for__user(
    user,
) -> List[Customer]:

    """ 
    list_of_employee_manager_contract_for_logged_in_user = (
        EmployeeManagerContract.objects.filter(
            contract__employee=user.employee, can_give_manager_role=True
        ).distinct("contract__customer")
    )
    """

    list_of_employee_manager_contract_for_logged_in_user = (
        EmployeeManagerContract.objects.filter(
            contract__employee=user.employee,
            can_give_manager_role=True,
            contract__customer__in=EmployeeManagerContract.objects.filter(
                contract__employee=user.employee,
                can_give_manager_role=True
            ).values_list('contract__customer', flat=True).distinct()
        )
    )


    # get the list of customers the employee manager is responsible for using the list_of_employee_manager_contract_for_logged_in_user
    return get__list_of_customers__for__list_of_employee_manager_contracts(
        list_of_employee_manager_contract_for_logged_in_user
    )


def get__list_of_customers__for__list_of_employee_manager_contracts(
    list_of_employee_manager_contracts: List[EmployeeManagerContract],
) -> List[Customer]:

    # get the list of customers the employee manager is responsible for using the list_of_employee_manager_contract_for_logged_in_user
    list_of_customers__for__employee_manager_contract = []
    for contract in list_of_employee_manager_contracts:
        list_of_customers__for__employee_manager_contract.append(
            contract.contract.customer
        )

    # order customers by created_at
    # created is a datetime field
    list_of_customers__for__employee_manager_contract.sort(
        key=lambda x: x.created_at, reverse=False
    )

    return list_of_customers__for__employee_manager_contract


# TODO add tests for this function and if it works correctly replace the part of the other fuctions that are looking for employee manager contracts
def get__list_of_employee_manager_contract__with__given_abitly__for__user(
    user, ability
) -> List[EmployeeManagerContract]:

    """ 
    return EmployeeManagerContract.objects.filter(
        contract__employee=user.employee, **{ability: True}
    ).distinct("contract__customer")
    """

    return EmployeeManagerContract.objects.filter(
        contract__employee=user.employee,
        **{ability: True},
        contract__customer__in=EmployeeManagerContract.objects.filter(
            contract__employee=user.employee,
            **{ability: True}
        ).values_list('contract__customer', flat=True).distinct()
    )


def check__employee_manager_contract__exists__for__employee_manager_and_customer__and__can_add_users__and__is_active(
    employee_manager: Employee, customer: Customer
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
    list_of_customer_program_executions: QuerySet,
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
    list_of_active_NadooitApiKey = get__list_of_all_NadooitApiKey__for__user(
        user, is_active=True
    )

    # Set all the active NadooitApiKey to inactive
    for active_NadooitApiKey in list_of_active_NadooitApiKey:
        active_NadooitApiKey.is_active = False
        active_NadooitApiKey.save()


def get__list_of_all_NadooitApiKey__for__user(user: User, is_active=True) -> QuerySet:
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


def get__customer__for__customer_program_execution_id(
    customer_program_execution_id,
) -> Customer | None:

    customer_program_execution = (
        get__customer_program_execution__for__customer_program_execution_id(
            customer_program_execution_id
        )
    )

    print("customer_program_execution", customer_program_execution)

    if customer_program_execution is not None:
        return customer_program_execution.customer_program.customer
    else:
        return None


def check__customer_program_execution__exists__for__customer_program_execution_id(
    customer_program_execution_id,
) -> bool:
    return CustomerProgramExecution.objects.filter(
        id=customer_program_execution_id
    ).exists()


def get__customer_program_execution__for__customer_program_execution_id(
    customer_program_execution_id,
) -> CustomerProgramExecution | None:
    return CustomerProgramExecution.objects.filter(
        id=customer_program_execution_id
    ).first()


def set__payment_status__for__customer_program_execution(
    customer_program_execution: CustomerProgramExecution,
    payment_status: str,
):
    customer_program_execution.payment_status = payment_status
    customer_program_execution.save()


def get__payment_status__for__customer_program_execution(
    customer_program_execution: CustomerProgramExecution,
) -> str:
    return customer_program_execution.payment_status


def create__customer_program_execution_complaint__for__customer_program_execution_and_complaint_and_employee(
    customer_program_execution: CustomerProgramExecution,
    complaint: str,
    employee: Employee,
) -> Complaint | None:
    try:
        complaint = Complaint.objects.create(
            customer_program_execution=customer_program_execution,
            complaint=complaint,
            customer_program_execution_manager=employee,
        )
        return complaint
    except Exception as e:
        print("error creating complaint", e)
        return None


def get__list_of_customers_the_employee_has_a_customer_program_manager_contract_with_and_can_create_such_a_contract(
    employee: Employee,
) -> list[Customer]:

    list_of_customers_the_manager_is_responsible_for = []

    """ 
    # order by updated_at
    list_of_employee_manager_contract_for_logged_in_user = (
        CustomerProgramManagerContract.objects.filter(
            contract__employee=employee,
            can_give_manager_role=True,
        ).distinct("contract__customer")
    )
    """
    
    # order by updated_at
    list_of_employee_manager_contract_for_logged_in_user = (
        CustomerProgramManagerContract.objects.filter(
            contract__employee=employee,
            can_give_manager_role=True,
            contract__customer__in=CustomerProgramManagerContract.objects.filter(
                contract__employee=employee,
                can_give_manager_role=True
            ).values_list('contract__customer', flat=True).distinct()
        ).order_by('-contract__updated_at')
    )

    # get the list of customers the customer program manager is responsible for using the list_of_employee_manager_contract_for_logged_in_user
    list_of_customers_the_manager_is_responsible_for = []
    for contract in list_of_employee_manager_contract_for_logged_in_user:
        list_of_customers_the_manager_is_responsible_for.append(
            contract.contract.customer
        )

    return list_of_customers_the_manager_is_responsible_for


def get__employee__for__employee_id(employee_id) -> Employee | None:
    return Employee.objects.filter(id=employee_id).first()


def get__csv__for__list_of_customer_program_executions(
    list_of_customer_program_executions: list[CustomerProgramExecution],
) -> HttpResponse:

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="transactions.csv"'

    writer = csv.writer(response)

    # write the header
    writer.writerow(["id", "Programmname", "erspaarte Zeit", "Preis", "Erstellt"])

    for transaction in list_of_customer_program_executions:

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


def check__user_is_allowed_to_add_new_key(user: User) -> bool:

    # user is superuser
    if user.is_superuser:
        return True
    # user is not superuser
    else:
        return False


def get__user_info__for__user(user: User) -> dict:
    return {
        "user_code": user.user_code,
        "display_name": user.display_name,
    }


""" 
def get__list_of_manager_contracts__for__employee(employee: Employee):

    # This function returns a list of all *_manager_contracts the employee has.
    # This function needs to be updated if a new *_manager_contract is added.

    list_of_manager_contracts = []

    # get all employee contracts for the employee
    list_of_employee_contracts = EmployeeContract.objects.filter(
        employee=employee
    ).order_by("created_at")

    # for each employee contract get all the manager contracts
    for employee_contract in list_of_employee_contracts:
        list_of_manager_contracts.append(
            {
                "employee_contract": employee_contract,
                "list_of_manager_contracts_with_abilities": [
                    EmployeeManagerContract.objects.filter(
                        contract=employee_contract
                    ).first(),
                    
                    CustomerProgramManagerContract.objects.filter(
                        contract=employee_contract
                    ).first(),
                    CustomerManagerContract.objects.filter(
                        contract=employee_contract
                    ).first(),
                ],
            }
        )

    logger.debug(list_of_manager_contracts)

    # remove None values without changing the order of the list
    for manager_contract in list_of_manager_contracts:
        manager_contract["list_of_manager_contracts"] = list(
            filter(None, manager_contract["list_of_manager_contracts"])
        )
    logger.debug("THIS IS WHAT IT LOOKS LIKE BEFORE GETTING THE ABILITIES")
    logger.debug(list_of_manager_contracts)

    # next we need to get all the abilities the employee has per manager contract. Each contract has a get_abilities() function that returns a list of abilities.
    # This list then gets added to the dict along with the contract
    for manager_contract in list_of_manager_contracts:	
        
        # get the list of abilities for the contract
        list_of_abilities = []
        for contract in manager_contract["list_of_manager_contracts"]:
            list_of_abilities.append(contract.get_abilities())

        # add the list of abilities to the dict
       
            


    logger.debug("THIS IS WHAT IT LOOKS LIKE AT THE END")
    logger.debug(list_of_manager_contracts)

    # return the list of manager contracts
    return list_of_manager_contracts
 """


def get__list_of_manager_contracts__for__employee(employee: Employee):
    """
    results in the following structure:
        [
            {
                'employee_contract': <EmployeeContract: Angestelltenvertrag zwischen: NADOOIT Christoph Backhaus - Christoph Backhaus IT>,
                'list_of_manager_contracts':
                [
                    {
                    'manager_contract': <EmployeeManagerContract: Angestelltenverwaltervertrag zwischen: NADOOIT Christoph Backhaus - Christoph Backhaus IT>,
                    },
                    {
                    'manager_contract': <CustomerProgramManagerContract: Kundenverwaltervertrag zwischen: NADOOIT Christoph Backhaus - Christoph Backhaus IT>,
                    },
                    {
                    'manager_contract': <CustomerManagerContract: Kundenverwaltervertrag zwischen: NADOOIT Christoph Backhaus - Christoph Backhaus IT>,
                    }
                ]
            }
            {
                'employee_contract': <EmployeeContract: Angestelltenvertrag zwischen: NADOOIT Christoph Backhaus - Christoph Backhaus IT>,
                'list_of_manager_contracts': []
            }
            ]
    """

    list_of_manager_contracts = []

    # get all employee contracts for the employee
    list_of_employee_contracts = EmployeeContract.objects.filter(
        employee=employee
    ).order_by("created_at")

    # for each employee contract get all the manager contracts
    for employee_contract in list_of_employee_contracts:

        # create a list of all the manager contracts for the employee contract
        # this list will be added to the dict
        # if there is no manager contract for an employee_contract the value for list_of_manager_contracts will be an empty list

        list_of_manager_contracts_for_employee_contract = []
        list_of_manager_contracts_for_employee_contract.append(
            {
                "manager_contract": EmployeeManagerContract.objects.filter(
                    contract=employee_contract
                ).first(),
            }
        )
        list_of_manager_contracts_for_employee_contract.append(
            {
                "manager_contract": CustomerProgramManagerContract.objects.filter(
                    contract=employee_contract
                ).first(),
            }
        )
        list_of_manager_contracts_for_employee_contract.append(
            {
                "manager_contract": CustomerManagerContract.objects.filter(
                    contract=employee_contract
                ).first(),
            },
        )

        # remove None values without changing the order of the list
        list_of_manager_contracts_for_employee_contract = list(
            filter(None, list_of_manager_contracts_for_employee_contract)
        )

        # remove all items from the list where manager_contract is None
        list_of_manager_contracts_for_employee_contract = [
            item
            for item in list_of_manager_contracts_for_employee_contract
            if item["manager_contract"] is not None
        ]

        # add the employee contract and the list of manager contracts to the list of manager contracts
        list_of_manager_contracts.append(
            {
                "employee_contract": employee_contract,
                "list_of_manager_contracts": list_of_manager_contracts_for_employee_contract,
            }
        )

    logger.debug(list_of_manager_contracts)

    # return the list of manager contracts
    return list_of_manager_contracts
