import datetime
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
def test_get__not_paid_customer_program_executions__for__filter_type_and_cutomer_id(
    customer_program,
):
    # Arrange
    filter_type = "last20"
    filter_type = "lastmonth"
    filter_type = "today"
    filter_type = "thismonth"
    filter_type = "thisyear"

    # Create customer program executions for the customer program
    # Create 5 customer program executions for the customer program for today, this month and this year, and 1 for last month
    for i in range(5):
        model_bakery.baker.make(
            "nadooit_os.CustomerProgramExecution",
            customer_program=customer_program,
            execution_date=datetime.now(),
        )

    # Create 5 customer program executions for the customer program for last month
    for i in range(5):
        model_bakery.baker.make(
            "nadooit_os.CustomerProgramExecution",
            customer_program=customer_program,
            # Get the month of the current date and subtract 1 from it
            execution_date=datetime.now().replace(month=datetime.now().month - 1),
        )

    # Create 5 customer program executions for the customer program for last 20 days

    # Act
    # Assert
    assert True


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
