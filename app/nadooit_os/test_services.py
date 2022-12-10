import model_bakery
import pytest
from nadooit_os.services import (
    check__customer_program__for__customer_program_id__exists,
)

from nadooit_crm.models import Customer
from nadooit_program.models import Program
from nadooit_program_ownership_system.models import CustomerProgram
from nadooit_auth.models import User
from model_bakery import baker

from nadooit_os.services import (
    check__user__is__customer_program_manager__for__customer_prgram,
)

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
    user: User, customer_program: CustomerProgram
):
    # Arrange
    baker.make("nadooit_hr.Employee", user=user)
    baker.make(
        "nadooit_hr.CustomerProgramManagerContract",
        contract=baker.make(
            "nadooit_hr.EmployeeContract",
            employee=user.employee,
            customer=customer_program.customer,
        ),
    )
    # Act
    # Assert
    assert (
        check__user__is__customer_program_manager__for__customer_prgram(
            user, customer_program
        )
        == True
    )


@pytest.mark.django_db
def test_check__customer_program__for__customer_program_id__exists(customer_program):
    # Arrange
    # Act
    # Assert
    assert (
        check__customer_program__for__customer_program_id__exists(
            customer_program_id=customer_program.id
        )
        == True
    )
