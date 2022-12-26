from datetime import datetime
import model_bakery
import pytest
from nadooit_os.services import (
    get__list_of_customers__for__employee_that_has_a_time_account_manager_contract_with_and_can_create_time_account_manager_contracts_for_them,
)
from nadooit_hr.models import TimeAccountManagerContract
from nadooit_os.services import (
    create__time_account_manager_contract__for__user_code_customer_and_list_of_abilities_according_to_employee_creating_contract,
)
from nadooit_os.services import (
    check__user__exists__for__user_code,
    set__all_active_NadooitApiKey__for__user_to_inactive,
)
from nadooit_api_key.models import NadooitApiKey
from nadooit_os.services import create__NadooitApiKey__for__user
from nadooit_os.services import (
    get__customer_time_accounts_grouped_by_customer_with_total_time_of_all_time_accounts__for__employee,
)
from nadooit_os.services import (
    get__list_of_customer_time_accounts__for__list_of_TimeAccountMangerContracts,
)
from nadooit_os.services import get__active_TimeAccountManagerContracts__for__employee
from nadooit_os.services import (
    get__time_as_string_in_hour_format__for__time_in_seconds_as_integer,
    get__price_as_string_in_euro_format__for__price_in_euro_as_decimal,
    get__not_paid_customer_program_executions__for__filter_type_and_cutomer_id,
    check__customer_program__for__customer_program_id__exists,
)
from nadooit_api_executions_system.models import CustomerProgramExecution


from nadooit_crm.models import Customer
from nadooit_program.models import Program
from nadooit_program_ownership_system.models import CustomerProgram
from nadooit_auth.models import User
from model_bakery import baker

from nadooit_os.services import (
    check__user__is__customer_program_manager__for__customer_prgram,
)
import uuid

# A pytest fixure that returns a user object
@pytest.fixture
def user():
    return User.objects.create(
        username="test",
        display_name="test",
    )


@pytest.fixture()
def employee_with_active_TimeAccountManagerContract():
    employee = baker.make("nadooit_hr.Employee")
    employeecontract = baker.make("nadooit_hr.EmployeeContract", employee=employee)
    baker.make(
        "nadooit_hr.TimeAccountManagerContract",
        contract=employeecontract,
        can_give_manager_role=True,
        can_delete_time_accounts=True,
        can_create_time_accounts=True,
    )
    return employee


@pytest.fixture()
def customer():
    return baker.make("nadooit_crm.Customer", name="Customer 1")


@pytest.fixture()
def employee_with_active_TimeAccountManagerContract_and_also_managing_time_accounts_with_a_balance():
    employee = baker.make(
        "nadooit_hr.Employee",
        user=baker.make("nadooit_auth.User", is_active=True, user_code="TEST01"),
    )
    for i in range(5):

        customer = baker.make("nadooit_crm.Customer", name=f"Customer {i}")

        employeecontract = baker.make(
            "nadooit_hr.EmployeeContract", employee=employee, customer=customer
        )
        TimeAccountMangerContract = baker.make(
            "nadooit_hr.TimeAccountManagerContract",
            contract=employeecontract,
            can_give_manager_role=True,
            can_delete_time_accounts=True,
            can_create_time_accounts=True,
        )
        for x in range(5):
            baker.make(
                "nadooit_time_account.CustomerTimeAccount",
                customer=TimeAccountMangerContract.contract.customer,
                name=f"TimeAccountMangerContract {i}",
                time_account=baker.make(
                    "nadooit_time_account.TimeAccount", time_balance_in_seconds=90000
                ),
            )

    return employee


@pytest.fixture()
def list_of_TimeAccountMangerContracts__without_CustomerTimeAccounts():
    list_of_TimeAccountMangerContracts = []
    for i in range(5):
        employee = baker.make("nadooit_hr.Employee")
        employeecontract = baker.make("nadooit_hr.EmployeeContract", employee=employee)
        TimeAccountMangerContract = baker.make(
            "nadooit_hr.TimeAccountManagerContract",
            contract=employeecontract,
            can_give_manager_role=True,
            can_delete_time_accounts=True,
            can_create_time_accounts=True,
        )
        list_of_TimeAccountMangerContracts.append(TimeAccountMangerContract)
    return list_of_TimeAccountMangerContracts


@pytest.fixture()
def employee_with_active_TimeAccountManagerContract_and_the_right_to_create_time_account_manager_contracts():
    employee = baker.make(
        "nadooit_hr.Employee",
        user=baker.make(
            "nadooit_auth.User",
            is_active=True,
            user_code="TEST01",
            display_name="Test Employee",
        ),
    )
    test_customer = baker.make("nadooit_crm.Customer", name="Test Customer")
    employeecontract = baker.make(
        "nadooit_hr.EmployeeContract", employee=employee, customer=test_customer
    )
    baker.make(
        "nadooit_hr.TimeAccountManagerContract",
        contract=employeecontract,
        can_give_manager_role=True,
        can_delete_time_accounts=True,
        can_create_time_accounts=True,
    )
    return employee


@pytest.fixture()
def list_of_TimeAccountMangerContracts__with_CustomerTimeAccounts():
    list_of_TimeAccountMangerContracts = []
    for i in range(5):
        employee = baker.make("nadooit_hr.Employee")
        employeecontract = baker.make("nadooit_hr.EmployeeContract", employee=employee)
        TimeAccountMangerContract = baker.make(
            "nadooit_hr.TimeAccountManagerContract",
            contract=employeecontract,
            can_give_manager_role=True,
            can_delete_time_accounts=True,
            can_create_time_accounts=True,
        )
        baker.make(
            "nadooit_time_account.CustomerTimeAccount",
            customer=TimeAccountMangerContract.contract.customer,
        )
        list_of_TimeAccountMangerContracts.append(TimeAccountMangerContract)
    return list_of_TimeAccountMangerContracts


@pytest.fixture()
def employee_with_no_active_TImeAccountManagerContract():
    employee = baker.make("nadooit_hr.Employee")

    return employee


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
    customer_program: CustomerProgram,
):
    # Arrange
    filter_type = "last20"
    filter_type = "lastmonth"
    filter_type = "today"
    filter_type = "thismonth"
    filter_type = "thisyear"

    # Create customer program executions for the customer program
    # Create 5 customer program executions for the customer program for today, this month and this year, and 1 for last month

    list_of_executions_this_year = []
    list_of_executions_this_month = []
    list_of_executions_today = []
    list_of_executions_last_month = []
    list_of_the_last_20_executions = []

    # Create a random datetime for the past month
    import pytz

    utc = pytz.utc
    now_but_a_month_ago = utc.localize(
        datetime.utcnow().replace(month=datetime.utcnow().month - 1)
    )

    # Create a couple lines of empty space for readability
    print("	")
    print("	")
    print("	")

    # Print the date for the past month
    print("The date for the past month is: ")
    print(now_but_a_month_ago)
    # Create 5 customer program executions for the customer program for last month
    for i in range(5):

        new_exectuion: CustomerProgramExecution = baker.make(
            "nadooit_api_executions_system.CustomerProgramExecution",
            customer_program=customer_program,
        )
        new_exectuion.created_at = now_but_a_month_ago
        new_exectuion.save()

        list_of_executions_last_month.append(new_exectuion)
        list_of_the_last_20_executions.append(new_exectuion)
        if new_exectuion.created_at.year == datetime.now().year:
            list_of_executions_this_year.append(new_exectuion)
    print("	")
    print(len(list_of_the_last_20_executions))
    # customer program executions for today
    for i in range(15):

        new_exectuion = baker.make(
            "nadooit_api_executions_system.CustomerProgramExecution",
            customer_program=customer_program,
        )

        list_of_executions_today.append(new_exectuion)
        list_of_the_last_20_executions.append(new_exectuion)
        list_of_executions_this_month.append(new_exectuion)
        list_of_executions_this_year.append(new_exectuion)

    print("    ")
    print(len(list_of_the_last_20_executions))
    print("	")
    # Act
    # Assert
    filter_type = "lastmonth"
    assert len(
        list(
            get__not_paid_customer_program_executions__for__filter_type_and_cutomer_id(
                filter_type, customer_program.customer.id
            )
        )
    ) == len(list_of_executions_last_month)
    filter_type = "today"
    assert len(
        list(
            get__not_paid_customer_program_executions__for__filter_type_and_cutomer_id(
                filter_type, customer_program.customer.id
            )
        )
    ) == len(list_of_executions_today)
    filter_type = "thismonth"
    assert len(
        list(
            get__not_paid_customer_program_executions__for__filter_type_and_cutomer_id(
                filter_type, customer_program.customer.id
            )
        )
    ) == len(list_of_executions_this_month)
    filter_type = "thisyear"
    assert len(
        list(
            get__not_paid_customer_program_executions__for__filter_type_and_cutomer_id(
                filter_type, customer_program.customer.id
            )
        )
    ) == len(list_of_executions_this_year)
    filter_type = "last20"
    assert len(
        list(
            get__not_paid_customer_program_executions__for__filter_type_and_cutomer_id(
                filter_type, customer_program.customer.id
            )[:20]
        )
    ) == len(list_of_the_last_20_executions)


def test_get__price_as_string_in_euro_format__for__price_in_euro_as_decimal():
    # Arrange
    price_in_euro_as_decimal = 10.0
    # Act
    # Assert
    assert (
        get__price_as_string_in_euro_format__for__price_in_euro_as_decimal(
            price_in_euro_as_decimal
        )
        == "10,000 €"
    )
    price_in_euro_as_decimal = 10
    assert (
        get__price_as_string_in_euro_format__for__price_in_euro_as_decimal(
            price_in_euro_as_decimal
        )
        == "10,000 €"
    )
    price_in_euro_as_decimal = 10.000
    assert (
        get__price_as_string_in_euro_format__for__price_in_euro_as_decimal(
            price_in_euro_as_decimal
        )
        == "10,000 €"
    )
    price_in_euro_as_decimal = 10.00
    assert (
        get__price_as_string_in_euro_format__for__price_in_euro_as_decimal(
            price_in_euro_as_decimal
        )
        == "10,000 €"
    )
    price_in_euro_as_decimal = 10.00
    assert (
        get__price_as_string_in_euro_format__for__price_in_euro_as_decimal(
            price_in_euro_as_decimal
        )
        == "10,000 €"
    )
    price_in_euro_as_decimal = 10.0006
    assert (
        get__price_as_string_in_euro_format__for__price_in_euro_as_decimal(
            price_in_euro_as_decimal
        )
        == "10,001 €"
    )
    price_in_euro_as_decimal = 10.0003
    assert (
        get__price_as_string_in_euro_format__for__price_in_euro_as_decimal(
            price_in_euro_as_decimal
        )
        == "10,000 €"
    )


def test_get__time_as_string_in_hour_format__for__time_in_seconds_as_integer():
    # Arrange
    time_in_seconds_as_integer = 90185
    # Act
    time_as_string_in_hour_format = (
        get__time_as_string_in_hour_format__for__time_in_seconds_as_integer(
            time_in_seconds_as_integer
        )
    )
    # Assert
    assert time_as_string_in_hour_format == "25 std : 3 min : 5 sek"


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


@pytest.mark.django_db
def test_get__active_TimeAccountManagerContracts__for__employee___with__active_TimeAccountManagerContract(
    employee_with_active_TimeAccountManagerContract,
):
    # Arrange
    # Act
    # Assert
    assert (
        len(
            list(
                get__active_TimeAccountManagerContracts__for__employee(
                    employee_with_active_TimeAccountManagerContract
                )
            )
        )
        == 1
    )


@pytest.mark.django_db
def test_get__active_TimeAccountManagerContracts__for__employee__with__no_active_contract(
    employee_with_no_active_TImeAccountManagerContract,
):
    # Arrange
    # Act
    # Assert
    assert (
        len(
            list(
                get__active_TimeAccountManagerContracts__for__employee(
                    employee_with_no_active_TImeAccountManagerContract
                )
            )
        )
        == 0
    )


@pytest.mark.django_db
def test_get__list_of_customer_time_accounts__for__list_of_TimeAccountMangerContracts__with_CustomerTimeAccounts(
    list_of_TimeAccountMangerContracts__with_CustomerTimeAccounts,
):
    # Arrange
    # Act
    # Assert
    assert (
        len(
            list(
                get__list_of_customer_time_accounts__for__list_of_TimeAccountMangerContracts(
                    list_of_TimeAccountMangerContracts__with_CustomerTimeAccounts
                )
            )
        )
        == 5
    )


@pytest.mark.django_db
def test_get__list_of_customer_time_accounts__for__list_of_TimeAccountMangerContracts__with_no_CustomerTimeAccounts(
    list_of_TimeAccountMangerContracts__without_CustomerTimeAccounts,
):
    # Arrange
    # Act
    # Assert
    assert (
        len(
            list(
                get__list_of_customer_time_accounts__for__list_of_TimeAccountMangerContracts(
                    list_of_TimeAccountMangerContracts__without_CustomerTimeAccounts
                )
            )
        )
        == 0
    )


# TODO This test does not work. Figure out how to test this
@pytest.mark.django_db
def test_get__customer_time_accounts_grouped_by_customer_with_total_time_of_all_time_accounts__for__employee(
    employee_with_active_TimeAccountManagerContract_and_also_managing_time_accounts_with_a_balance,
):
    # Arrange
    # Act
    customer_time_accounts_grouped_by_customer_with_total_time_of_all_time_accounts = get__customer_time_accounts_grouped_by_customer_with_total_time_of_all_time_accounts__for__employee(
        employee_with_active_TimeAccountManagerContract_and_also_managing_time_accounts_with_a_balance
    )

    """     print(
            customer_time_accounts_grouped_by_customer_with_total_time_of_all_time_accounts
        )
    """
    # Assert
    assert True


@pytest.mark.django_db
def test_create__NadooitApiKey__for__user(user):
    # Arrange
    # Act
    nadooit_api_key = create__NadooitApiKey__for__user(user)

    fake_api_key = uuid.uuid4()

    nadooit_api_key_2 = create__NadooitApiKey__for__user(user, fake_api_key)

    # Assert

    assert type(nadooit_api_key) == NadooitApiKey
    assert (
        type(nadooit_api_key_2) == NadooitApiKey
        and nadooit_api_key_2.api_key == fake_api_key
    )


@pytest.mark.django_db
def test_create__time_account_manager_contract__for__user_code_customer_and_list_of_abilities_according_to_employee_creating_contract(
    user,
    employee_with_active_TimeAccountManagerContract_and_the_right_to_create_time_account_manager_contracts,
):

    # Arrange

    """
    ability == "can_create_time_accounts",
    "can_delete_time_accounts",
    "can_give_manager_role"
    """

    list_of_abilities = [
        "can_create_time_accounts",
        "can_delete_time_accounts",
        "can_give_manager_role",
    ]

    time_account_manager_contract = TimeAccountManagerContract.objects.get(
        contract__employee=employee_with_active_TimeAccountManagerContract_and_the_right_to_create_time_account_manager_contracts
    )

    customer = time_account_manager_contract.contract.customer

    # Act
    time_account_manager_contract = create__time_account_manager_contract__for__user_code_customer_and_list_of_abilities_according_to_employee_creating_contract(
        user_code=user.user_code,
        customer=customer,
        list_of_abilities=list_of_abilities,
        employee_creating_contract=employee_with_active_TimeAccountManagerContract_and_the_right_to_create_time_account_manager_contracts,
    )
    # Assert
    assert type(time_account_manager_contract) == TimeAccountManagerContract
    assert time_account_manager_contract.contract.employee == user.employee
    assert time_account_manager_contract.contract.customer == customer
    assert time_account_manager_contract.can_create_time_accounts == True
    assert time_account_manager_contract.can_delete_time_accounts == True
    assert time_account_manager_contract.can_give_manager_role == True


@pytest.mark.django_db
def test_check__user__exists__for__user_code(user):
    # Arrange
    fake_user_code = "NADOO01"
    # Act
    # Assert
    assert check__user__exists__for__user_code(user_code=user.user_code) == True
    assert check__user__exists__for__user_code(user_code=fake_user_code) == False


@pytest.mark.django_db
def test_set__all_active_NadooitApiKey__for__user_to_inactive(user):
    # Arrange
    baker.make(NadooitApiKey, user=user, is_active=True)
    baker.make(NadooitApiKey, user=user, is_active=True)

    # Act

    set__all_active_NadooitApiKey__for__user_to_inactive(user)

    # Assert

    assert NadooitApiKey.objects.filter(user=user, is_active=True).count() == 0


@pytest.mark.django_db
def test_get__list_of_customers__for__employee_that_has_a_time_account_manager_contract_with_and_can_create_time_account_manager_contracts_for_them(
    employee_with_active_TimeAccountManagerContract_and_the_right_to_create_time_account_manager_contracts,
):
    # Arrange
    # Act
    # Assert
    assert (
        len(
            get__list_of_customers__for__employee_that_has_a_time_account_manager_contract_with_and_can_create_time_account_manager_contracts_for_them(
                employee_with_active_TimeAccountManagerContract_and_the_right_to_create_time_account_manager_contracts
            )
        )
        == 1
    )
