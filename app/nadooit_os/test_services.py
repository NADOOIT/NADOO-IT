from nadooit_time_account.models import TimeAccount
import nadooit_time_account.models
import pytest
from nadooit_os.services import (
    create__customer_program_execution__for__customer_program,
)
from nadooit_hr.models import Employee

from nadooit_crm.models import Customer
from nadooit_program.models import Program
from nadooit_program_ownership_system.models import CustomerProgram
from nadooit_auth.models import User

from nadooit_os.services import (
    check__user__is__customer_program_manager__for__customer_prgram,
)
from nadooit_hr.models import CustomerProgramManagerContract, EmployeeContract


from model_bakery import baker


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
def test_check__user__is__customer_program_manager__for__customer_prgram():
    print("Is this run first?")
    # Arrange
    # Act
    # Assert

    user = baker.make(User)

    baker.make(Employee, user=user)

    customer = baker.make(Customer)

    CustomerProgramManagerContract.objects.create(
        contract=EmployeeContract.objects.create(
            employee=user.employee,
            customer=customer,
        ),
    )

    customer_program = baker.make(CustomerProgram, customer=customer)

    assert (
        check__user__is__customer_program_manager__for__customer_prgram(
            user, customer_program
        )
        == True
    )


@pytest.mark.django_db
def test_create__customer_program_execution__for__customer_program():

    customer = baker.make(Customer)

    customer_program = baker.make(
        CustomerProgram,
        customer=customer,
        program=baker.make(Program, name="test"),
        time_account=baker.make(TimeAccount, time_balance_in_seconds=0),
    )

    create__customer_program_execution__for__customer_program(customer_program)
