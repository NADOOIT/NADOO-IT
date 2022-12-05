import pytest
from nadooit_hr.models import Employee

from nadooit_crm.models import Customer
from nadooit_program.models import Program
from nadooit_program_ownership_system.models import CustomerProgram
from nadooit_auth.models import User

from nadooit_os.services import (
    check__user__is__customer_program_manager__for__customer_prgram,
)
from nadooit_hr.models import CustomerProgramManagerContract, EmployeeContract

# A pytest fixure that returns a user object
@pytest.fixture
def user():
    return User.objects.create(
        username="test",
        display_name="test",
    )


# A pytest fixure that returns a customer program object
@pytest.fixture
def customer_program():
    return CustomerProgram.objects.create(
        customer=Customer.objects.create(
            name="test",
        ),
        program=Program.objects.create(
            name="test",
            description="test",
        ),
    )


@pytest.mark.django_db
def test_check__user__is__customer_program_manager__for__customer_prgram(
    user, customer_program
):
    print("Is this run first?")
    # Arrange
    # Act
    # Assert

    Employee.objects.create(
        user=user,
    )

    employee_contract = EmployeeContract.objects.create(
        employee=user.employee,
        customer=customer_program.customer,
    )

    CustomerProgramManagerContract.objects.create(
        contract=employee_contract,
    )

    assert (
        check__user__is__customer_program_manager__for__customer_prgram(
            user, customer_program
        )
        == True
    )
