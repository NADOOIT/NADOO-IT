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
def set__employee_contract__is_active__for__employee_contract_id(
    employee_contract_id, contract_state
) -> EmployeeContract:
    employee_contract = EmployeeContract.objects.get(id=employee_contract_id)
    employee_contract.is_active = contract_state
    employee_contract.deactivation_date = None
    employee_contract.save()
    return employee_contract


# Returns the employee contract for the given employee contract id
def get__employee_contract__for__employee_contract_id(employee_contract_id):
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
    employee_contract = EmployeeContract.objects.get(id=employee_contract_id)
    employee_contract.is_active = False
    employee_contract.deactivation_date = datetime.now()
    employee_contract.save()
    return employee_contract


# Checks if an employee contract exists for the given user code
def check__employee__exists__for__user_code(user_code) -> bool:
    return Employee.objects.filter(user__user_code=user_code).exists()


# Creates and returns a new employee  for the given user code
def create__employee__for__user_code(user_code) -> Employee:
    user = User.objects.get(user_code=user_code)
    employee = Employee.objects.create(user=user)
    return employee


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
