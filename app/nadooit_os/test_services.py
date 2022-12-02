import pytest
import os
from dotenv import load_dotenv

from nadooit_crm.models import Customer
from nadooit_program.models import Program
from nadooit_program_ownership_system.models import CustomerProgram
from nadooit_auth.models import User


@pytest.fixture(scope="session", autouse=True)
def load_env():
    print("Loading .env file")
    load_dotenv(
        r"C:\Users\ChristophBackhaus\OneDriveChristophBackhausIT\NADOOIT\Produkt-Abteilung\nadooit\Software\Dev\Server\managmentsystem\.env"
    )
    print(os.getenv("COCKROACH_DB_NAME"))


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
        name="test",
        description="test",
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
    # Arrange
    # Act
    # Assert
    assert check__user__is__customer_program_manager__for__customer_prgram() == True
