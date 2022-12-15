# This file contains the tests for the views of the nadooit app.

# The tests are written using pytest.
# The tests are run using the pytest-django plugin.
# The tests are run using the pytest-cov plugin.
# The tests are run using the pytest-mock plugin.

import pytest
from model_bakery import baker

from nadooit_os.views import get__employee_roles_and_rights__for__employee


@pytest.mark.django_db
def test_get__employee_roles_and_rights__for__employee__with__no_rights():
    # Arrange
    employee = baker.make("nadooit_hr.Employee")

    # Act
    roles_and_rights__for__user = get__employee_roles_and_rights__for__employee(
        employee
    )

    print(
        "roles_and_rights__for__user in Test for user with no rights",
        roles_and_rights__for__user,
    )

    # Assert
    assert roles_and_rights__for__user == {
        "is_time_account_manager": False,
        "user_is_Time_Account_Manager_and_can_give_manager_role": False,
        "is_api_key_manager": False,
        "user_is_api_key_manager_and_can_give_manager_role": False,
        "is_employee_manager": False,
        "user_is_Employee_Manager_and_can_give_Employee_Manager_role": False,
        "user_is_Employee_Manager_and_can_add_new_employee": False,
        "is_customer_program_manager": False,
        "user_is_Customer_Program_Manager_and_can_give_Customer_Program_Manager_role": False,
        "is_customer_program_execution_manager": False,
        "user_is_Customer_Program_Execution_Manager_and_can_give_Customer_Program_Execution_Manager_role": False,
    }


@pytest.mark.django_db
def test_get__employee_roles_and_rights__for__employee__with__all_rights_and_roles():
    # Arrange
    employee = baker.make(
        "nadooit_hr.Employee",
    )

    employeecontract = baker.make("nadooit_hr.EmployeeContract", employee=employee)
    baker.make(
        "nadooit_hr.TimeAccountManagerContract",
        contract=employeecontract,
        can_give_manager_role=True,
        can_delete_time_accounts=True,
        can_create_time_accounts=True,
    )
    baker.make(
        "nadooit_api_key.NadooitApiKeyManager",
        employee=employee,
        can_create_api_key=True,
        can_delete_api_key=True,
        can_give_manager_role=True,
    )
    baker.make(
        "nadooit_hr.EmployeeManagerContract",
        contract=employeecontract,
        can_add_new_employee=True,
        can_give_manager_role=True,
        can_delete_employee=True,
    )
    baker.make(
        "nadooit_hr.CustomerProgramManagerContract",
        contract=employeecontract,
        can_give_manager_role=True,
        can_delete_customer_program=True,
        can_create_customer_program=True,
    )
    baker.make(
        "nadooit_hr.CustomerProgramExecutionManagerContract",
        contract=employeecontract,
        can_create_customer_program_execution=True,
        can_delete_customer_program_execution=True,
        can_give_manager_role=True,
    )

    # Act
    roles_and_rights__for__user = get__employee_roles_and_rights__for__employee(
        employee
    )

    print(
        "roles_and_rights__for__user in Test for user with rights",
        roles_and_rights__for__user,
    )

    # Assert
    assert roles_and_rights__for__user == {
        "is_time_account_manager": True,
        "user_is_Time_Account_Manager_and_can_give_manager_role": True,
        "is_api_key_manager": True,
        "user_is_api_key_manager_and_can_give_manager_role": True,
        "is_employee_manager": True,
        "user_is_Employee_Manager_and_can_give_Employee_Manager_role": True,
        "user_is_Employee_Manager_and_can_add_new_employee": True,
        "is_customer_program_manager": True,
        "user_is_Customer_Program_Manager_and_can_give_Customer_Program_Manager_role": True,
        "is_customer_program_execution_manager": True,
        "user_is_Customer_Program_Execution_Manager_and_can_give_Customer_Program_Execution_Manager_role": True,
    }
