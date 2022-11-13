from nadooit_hr.models import EmployeeManagerContract
from nadooit_hr.models import Employee
from nadooit_hr.models import EmployeeContract
from nadooit_auth.models import User
from datetime import datetime

# Sets the employee contract as the given state
def set__employee_contract__is_active__for__employee_contract_id(
    employee_contract_id, contract_state
) -> EmployeeContract:
    employee_contract = EmployeeContract.objects.get(id=employee_contract_id)
    employee_contract.is_active = contract_state
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
def check__employee_contract__exists__for__user_code(user_code) -> bool:
    return Employee.objects.filter(user__user_code=user_code).exists()


# Checks if a user exists for the given user code
def check__user__exists__for__user_code(user_code) -> bool:
    return User.objects.filter(user_code=user_code).exists()


# Creates and returns a new employee  for the given user code
def create__employee__for__user_code(user_code) -> Employee:
    user = User.objects.get(user_code=user_code)
    employee = Employee.objects.create(user=user)
    return employee


# Returns the employee for the given user code
def get__employee__for__user_code(user_code) -> Employee:
    return Employee.objects.get(user__user_code=user_code)


def check__employee_manager_contract__exists__for__employee(employee) -> bool:
    return EmployeeManagerContract.objects.filter(contract__employee=employee).exists()
