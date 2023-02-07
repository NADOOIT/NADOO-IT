# confing for github copilot
# all tests are in the same file
# every test gets at least 2 asserts

from datetime import datetime, timedelta
from decimal import Decimal
from typing import Type
import model_bakery
import pytest
from nadooit_os.services import get__list_of_manager_contracts__for__employee
from nadooit_os.services import get__csv__for__list_of_customer_program_executions
from nadooit_os.services import get__employee_contract__for__employee_contract_id
from nadooit_os.services import (
    set__employee_contract__is_active_state__for__employee_contract_id,
    get__user_info__for__user,
)
from nadooit_hr.models import EmployeeContract
from nadooit_os.services import (
    set_employee_contract__as_inactive__for__employee_contract_id,
)
from nadooit_os.services import (
    get__list_of_customers__for__employee_manager_contract__that_can_give_the_role__for__user,
)
from nadooit_os.services import (
    create__employee_manager_contract__for__user_code_customer_and_list_of_abilities_according_to_employee_creating_contract,
    get__employee_manager_contract__for__user_code__and__customer,
)
from nadooit_os.services import (
    check__more_then_one_contract_between__user_code__and__customer,
)
from nadooit_os.services import get__employee_contract__for__user_code__and__customer
from nadooit_os.services import (
    check__employee_manager_contract__exists__for__employee_manager_and_customer__and__can_add_users__and__is_active,
)
from nadooit_hr.models import EmployeeManagerContract
from nadooit_os.services import (
    get__list_of_customers__and__their_employees__for__customers_that_have_a_employee_manager_contract__for__user,
)
from nadooit_os.services import (
    get__list_of_customers__for__employee_manager_contract__that_can_add_employees__for__user,
)
from nadooit_os.services import (
    get__list_of_customers_the_employee_has_a_customer_program_manager_contract_with_and_can_create_such_a_contract,
)
from nadooit_os.services import (
    set__list_of_abilities__for__customer_program_manager_contract_according_to_list_of_abilities,
)
from nadooit_os.services import (
    get__list_of_abilities__for__list_of_selected_abilities_and_list_of_possible_abilities_the_employee_can_give,
)
from nadooit_os.services import (
    get__list_of_abilties__for__customer_program_manager_contract,
)
from nadooit_os.services import (
    get__customer_program__for__customer_program_id,
    get__customer_program_manager_contract__for__employee_and_customer,
    get__next_price_level__for__customer_program,
)
from nadooit_hr.models import CustomerProgramManagerContract
from nadooit_os.services import (
    get__list_of_customers_the_employee_has_a_customer_program_execution_manager_contract_with_and_can_create_such_a_contract,
    get__list_of_customers_the_employee_has_a_customer_programm_manager_contract_with_and_the_customer_programms__for__employee,
)
from nadooit_os.services import (
    create__customer_program_execution_manager_contract__for__employee_and_customer_and_list_of_abilities_and_employee_with_customer_program_manager_contract,
    create__customer_program_execution_manager_contract__for__employee_contract,
)
from nadooit_os.services import get__employee__for__user_code
from nadooit_os.services import (
    create__customer_program_execution_complaint__for__customer_program_execution_and_complaint_and_employee,
)

from nadooit_os.services import get__payment_status__for__customer_program_execution
from nadooit_os.services import set__payment_status__for__customer_program_execution
from nadooit_os.services import (
    get__customer_program_execution__for__customer_program_execution_id,
)
from nadooit_os.services import get__customer__for__customer_program_execution_id
from nadooit_os.services import (
    check__customer_program_execution__exists__for__customer_program_execution_id,
)
from nadooit_os.services import (
    get__sum_of_price_for_execution__for__list_of_customer_program_exections,
)
from nadooit_os.services import (
    get__sum_of_time_saved_in_seconds__for__list_of_customer_program_exections,
)
from nadooit_os.services import (
    get__customer_program_executions__for__filter_type_and_customer,
)
from nadooit_os.services import (
    check__active_customer_program_execution_manager_contract__exists__between__employee_and_customer,
)
from nadooit_os.services import get__customer__for__customer_id
from nadooit_os.services import check__customer__exists__for__customer_id
from nadooit_os.services import (
    get__list_of_customer_program_execution__for__employee_and_filter_type__grouped_by_customer,
)
from nadooit_hr.models import CustomerProgramExecutionManagerContract, Employee
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
    get__not_paid_customer_program_executions__for__filter_type_and_customer,
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


@pytest.fixture
def customer_program_execution():
    return baker.make("nadooit_api_executions_system.CustomerProgramExecution")


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
def customer_with_customer_program_execution():
    customer = baker.make("nadooit_crm.Customer", name="Customer 1")
    customerprogram = baker.make(
        "nadooit_program_ownership_system.CustomerProgram", customer=customer
    )
    customerprogramexecution = baker.make(
        "nadooit_api_executions_system.CustomerProgramExecution",
        customer_program=customerprogram,
    )
    return customer


@pytest.fixture()
def employee_with_active_CustomerProgramExecutionManagerContract():
    employee = baker.make("nadooit_hr.Employee")
    employeecontract = baker.make("nadooit_hr.EmployeeContract", employee=employee)
    baker.make(
        "nadooit_hr.CustomerProgramExecutionManagerContract",
        contract=employeecontract,
        can_give_manager_role=True,
        can_delete_customer_program_execution=True,
        can_create_customer_program_execution=True,
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


def get__utc_datetime_for_first_of_last_month():
    import pytz

    utc = pytz.utc
    now_but_a_month_ago = None
    if datetime.utcnow().month == 1:
        now_but_a_month_ago = utc.localize(
            datetime.utcnow().replace(month=12, day=1, year=datetime.utcnow().year - 1)
        )
    else:
        now_but_a_month_ago = utc.localize(
            datetime.utcnow().replace(month=datetime.utcnow().month - 1, day=1)
        )
    return now_but_a_month_ago


@pytest.fixture()
def customer_program_executions():

    test_customer = baker.make(Customer, name="Test Customer")

    customer_program = CustomerProgram.objects.create(
        customer=test_customer,
        program=Program.objects.create(
            name="test",
            description="test",
        ),
    )

    list_of_executions_this_year = []
    list_of_executions_this_month = []
    list_of_executions_today = []
    list_of_executions_last_month = []
    list_of_the_last_20_executions = []

    # Create a random datetime for the past month
    import pytz

    utc = pytz.utc
    now_but_a_month_ago = get__utc_datetime_for_first_of_last_month()

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

    return (
        test_customer.customer.id,
        list_of_executions_today,
        list_of_the_last_20_executions,
        list_of_executions_this_month,
        list_of_executions_this_year,
    )


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
def test_get__not_paid_customer_program_executions__for__filter_type_and_customer(
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
    now_but_a_month_ago = get__utc_datetime_for_first_of_last_month()

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
        if new_exectuion.created_at.year == datetime.utcnow().year:
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
            get__not_paid_customer_program_executions__for__filter_type_and_customer(
                filter_type, customer_program.customer
            )
        )
    ) == len(list_of_executions_last_month)
    filter_type = "today"
    assert len(
        list(
            get__not_paid_customer_program_executions__for__filter_type_and_customer(
                filter_type, customer_program.customer
            )
        )
    ) == len(list_of_executions_today)
    filter_type = "thismonth"
    assert len(
        list(
            get__not_paid_customer_program_executions__for__filter_type_and_customer(
                filter_type, customer_program.customer
            )
        )
    ) == len(list_of_executions_this_month)
    filter_type = "thisyear"
    assert len(
        list(
            get__not_paid_customer_program_executions__for__filter_type_and_customer(
                filter_type, customer_program.customer
            )
        )
    ) == len(list_of_executions_this_year)
    filter_type = "last20"
    assert len(
        list(
            get__not_paid_customer_program_executions__for__filter_type_and_customer(
                filter_type, customer_program.customer
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


@pytest.mark.django_db
def test_get__list_of_customer_program_execution__for__employee_and_filter_type__grouped_by_customer():
    # Arrange

    # Create a customer, a program and 10 program executions for the customer
    customer = baker.make(Customer)
    program = baker.make(Program)
    customer_program = baker.make(CustomerProgram, customer=customer, program=program)
    for i in range(10):
        baker.make(
            CustomerProgramExecution,
            customer_program=customer_program,
        )

    # Create a second customer, a program and 10 program executions for the customer

    customer_2 = baker.make(Customer)
    program_2 = baker.make(Program)
    customer_program_2 = baker.make(
        CustomerProgram, customer=customer_2, program=program_2
    )
    for i in range(10):
        baker.make(
            CustomerProgramExecution,
            customer_program=customer_program_2,
        )

    # Create a user and an employee for the user, and a customer program execution mangager contract for the employee and the customer

    user = baker.make(User)
    employee = baker.make(Employee, user=user)
    baker.make(
        CustomerProgramExecutionManagerContract,
        contract__employee=employee,
        contract__customer=customer,
    )
    baker.make(
        CustomerProgramExecutionManagerContract,
        contract__employee=employee,
        contract__customer=customer_2,
    )

    # Act

    list_of_customer_program_execution__for__employee_and_filter_type__grouped_by_customer = get__list_of_customer_program_execution__for__employee_and_filter_type__grouped_by_customer(
        employee
    )

    print(
        "list_of_customer_program_execution__for__employee_and_filter_type__grouped_by_customer"
    )
    print(
        list_of_customer_program_execution__for__employee_and_filter_type__grouped_by_customer
    )

    # Assert
    assert (
        len(
            list_of_customer_program_execution__for__employee_and_filter_type__grouped_by_customer
        )
        == 2
    )


@pytest.mark.django_db
def test_check__customer__exists__for__customer_id(customer):
    # Arrange
    fake_customer_id = 999
    # Act
    # Assert
    assert check__customer__exists__for__customer_id(customer_id=customer.id) == True
    assert (
        check__customer__exists__for__customer_id(customer_id=fake_customer_id) == False
    )


@pytest.mark.django_db
def test_get__customer__for__customer_id(customer):
    # Arrange
    fake_customer_id = 999
    # Act
    # Assert
    assert get__customer__for__customer_id(customer_id=customer.id) == customer
    assert get__customer__for__customer_id(customer_id=fake_customer_id) == None


@pytest.mark.django_db
def test_check__active_customer_program_execution_manager_contract__exists__between__employee_and_customer(
    employee_with_active_CustomerProgramExecutionManagerContract,
):
    # Arrange
    # Act
    # Assert
    assert (
        check__active_customer_program_execution_manager_contract__exists__between__employee_and_customer(
            employee_with_active_CustomerProgramExecutionManagerContract,
            CustomerProgramExecutionManagerContract.objects.filter(
                contract__employee=employee_with_active_CustomerProgramExecutionManagerContract
            )
            .first()
            .contract.customer,
        )
    ) == True
    assert (
        check__active_customer_program_execution_manager_contract__exists__between__employee_and_customer(
            employee_with_active_CustomerProgramExecutionManagerContract,
            baker.make(Customer),
        )
        == False
    )


@pytest.mark.django_db
def test_get__customer_program_executions__for__filter_type_and_customer(
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

    list_of_executions_this_year = []
    list_of_executions_this_month = []
    list_of_executions_today = []
    list_of_executions_last_month = []
    list_of_the_last_20_executions = []

    # Create a random datetime for the past month
    import pytz

    now_but_a_month_ago = get__utc_datetime_for_first_of_last_month()

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
            get__customer_program_executions__for__filter_type_and_customer(
                filter_type, customer_program.customer
            )
        )
    ) == len(list_of_executions_last_month)
    filter_type = "today"
    assert len(
        list(
            get__customer_program_executions__for__filter_type_and_customer(
                filter_type, customer_program.customer
            )
        )
    ) == len(list_of_executions_today)
    filter_type = "thismonth"
    assert len(
        list(
            get__customer_program_executions__for__filter_type_and_customer(
                filter_type, customer_program.customer
            )
        )
    ) == len(list_of_executions_this_month)
    filter_type = "thisyear"
    assert len(
        list(
            get__customer_program_executions__for__filter_type_and_customer(
                filter_type, customer_program.customer
            )
        )
    ) == len(list_of_executions_this_year)
    filter_type = "last20"
    assert len(
        list(
            get__customer_program_executions__for__filter_type_and_customer(
                filter_type, customer_program.customer
            )[:20]
        )
    ) == len(list_of_the_last_20_executions)


@pytest.mark.django_db
def test_get__sum_of_time_saved_in_seconds__for__list_of_customer_program_exections(
    customer_program,
):
    # Arrange

    program_time_saved_in_seconds = 666

    for x in range(5):

        baker.make(
            "nadooit_api_executions_system.CustomerProgramExecution",
            customer_program=customer_program,
            program_time_saved_in_seconds=program_time_saved_in_seconds,
        )
    # Act
    # Assert
    assert (
        get__sum_of_time_saved_in_seconds__for__list_of_customer_program_exections(
            CustomerProgramExecution.objects.all()[:1]
        )
        == program_time_saved_in_seconds
    )
    assert (
        get__sum_of_time_saved_in_seconds__for__list_of_customer_program_exections(
            CustomerProgramExecution.objects.all()[:2]
        )
        == program_time_saved_in_seconds * 2
    )
    assert (
        get__sum_of_time_saved_in_seconds__for__list_of_customer_program_exections(
            CustomerProgramExecution.objects.all()[:3]
        )
        == program_time_saved_in_seconds * 3
    )


@pytest.mark.django_db
def test_get__sum_of_price_for_execution__for__list_of_customer_program_exections(
    customer_program,
):
    # Arrange

    price_for_execution = 666

    for x in range(5):
        baker.make(
            "nadooit_api_executions_system.CustomerProgramExecution",
            customer_program=customer_program,
            price_for_execution=price_for_execution,
        )
    # Act
    # Assert
    assert (
        get__sum_of_price_for_execution__for__list_of_customer_program_exections(
            CustomerProgramExecution.objects.all()[:1]
        )
        == price_for_execution
    )
    assert (
        get__sum_of_price_for_execution__for__list_of_customer_program_exections(
            CustomerProgramExecution.objects.all()[:2]
        )
        == price_for_execution * 2
    )
    assert (
        get__sum_of_price_for_execution__for__list_of_customer_program_exections(
            CustomerProgramExecution.objects.all()[:3]
        )
        == price_for_execution * 3
    )


@pytest.mark.django_db
def test_get__price_as_string_in_euro_format__for__price_in_euro_as_decimal():
    # Arrange
    price_in_euro_as_decimal = Decimal(666.66)
    # Act
    # Assert
    assert (
        get__price_as_string_in_euro_format__for__price_in_euro_as_decimal(
            price_in_euro_as_decimal
        )
        == "666,660 €"
    )
    assert (
        get__price_as_string_in_euro_format__for__price_in_euro_as_decimal(
            price_in_euro_as_decimal * 2
        )
        == "1.333,320 €"
    )
    assert (
        get__price_as_string_in_euro_format__for__price_in_euro_as_decimal(
            price_in_euro_as_decimal * 3
        )
        == "1.999,980 €"
    )


@pytest.mark.django_db
def test_check__customer_program_execution__exists__for__customer_program_execution_id(
    customer_program_execution,
):
    # Arrange
    # Act
    # Assert
    assert (
        check__customer_program_execution__exists__for__customer_program_execution_id(
            customer_program_execution.id
        )
        is True
    )
    assert (
        check__customer_program_execution__exists__for__customer_program_execution_id(
            uuid.uuid4()
        )
        is False
    )


@pytest.mark.django_db
def test_get__customer__for__customer_program_execution_id():
    # Arrange
    customer_program_execution = baker.make(
        "nadooit_api_executions_system.CustomerProgramExecution",
        customer_program=baker.make(
            CustomerProgram, customer=baker.make(Customer), program=baker.make(Program)
        ),
    )

    print(customer_program_execution)
    # Act
    # Assert
    assert (
        get__customer__for__customer_program_execution_id(customer_program_execution.id)
        == customer_program_execution.customer_program.customer
    )
    assert get__customer__for__customer_program_execution_id(uuid.uuid4()) is None


@pytest.mark.django_db
def test_get__customer_program_execution__for__customer_program_execution_id():
    # Arrange
    customer_program_execution = baker.make(
        "nadooit_api_executions_system.CustomerProgramExecution",
        customer_program=baker.make(
            CustomerProgram, customer=baker.make(Customer), program=baker.make(Program)
        ),
    )

    print(customer_program_execution)

    # Act
    # Assert
    assert (
        get__customer_program_execution__for__customer_program_execution_id(
            customer_program_execution.id
        )
        == customer_program_execution
    )
    assert (
        get__customer_program_execution__for__customer_program_execution_id(
            uuid.uuid4()
        )
        is None
    )


@pytest.mark.django_db
def test_set__payment_status__for__customer_program_execution():

    """
    class PaymentStatus(models.TextChoices):
    NOT_PAID = "NOT_PAID", _("Not Paid")
    PAID = "PAID", _("Paid")
    REFUNDED = "REFUNDED", _("Refunded")
    REVOKED = "REVOKED", _("Revoked")
    """

    # Arrange

    # create 3 customer_program_executions with different payment_status
    customer_program_execution_1 = baker.make(
        "nadooit_api_executions_system.CustomerProgramExecution",
        payment_status="NOT_PAID",
    )

    customer_program_execution_2 = baker.make(
        "nadooit_api_executions_system.CustomerProgramExecution",
        payment_status="PAID",
    )

    customer_program_execution_3 = baker.make(
        "nadooit_api_executions_system.CustomerProgramExecution",
        payment_status="REFUNDED",
    )

    customer_program_execution_4 = baker.make(
        "nadooit_api_executions_system.CustomerProgramExecution",
        payment_status="REVOKED",
    )

    # Act

    # set payment_status to PAID
    set__payment_status__for__customer_program_execution(
        customer_program_execution_1, "PAID"
    )

    # set payment_status to REFUNDED
    set__payment_status__for__customer_program_execution(
        customer_program_execution_2, "REFUNDED"
    )

    # set payment_status to REVOKED
    set__payment_status__for__customer_program_execution(
        customer_program_execution_3, "REVOKED"
    )

    # set payment_status to NOT_PAID
    set__payment_status__for__customer_program_execution(
        customer_program_execution_4, "NOT_PAID"
    )

    # Assert

    # check if payment_status is PAID
    assert (
        get__payment_status__for__customer_program_execution(
            customer_program_execution_1
        )
        == "PAID"
    )
    assert (
        get__payment_status__for__customer_program_execution(
            customer_program_execution_2
        )
        == "REFUNDED"
    )
    assert (
        get__payment_status__for__customer_program_execution(
            customer_program_execution_3
        )
        == "REVOKED"
    )
    assert (
        get__payment_status__for__customer_program_execution(
            customer_program_execution_4
        )
        == "NOT_PAID"
    )


@pytest.mark.django_db
def test_create__customer_program_execution_complaint__for__customer_program_execution_and_complaint_and_employee(
    customer_program_execution,
):
    # Arrange

    complaint = "complaint text"
    employee = baker.make("nadooit_hr.Employee")

    # Act
    customer_program_execution_complaint = create__customer_program_execution_complaint__for__customer_program_execution_and_complaint_and_employee(
        customer_program_execution, complaint, employee
    )
    # Assert
    assert (
        customer_program_execution_complaint.customer_program_execution
        == customer_program_execution
    )
    assert customer_program_execution_complaint.complaint == complaint
    assert (
        customer_program_execution_complaint.customer_program_execution_manager
        == employee
    )


@pytest.mark.django_db
def test_get__employee__for__user_code():
    # Arrange
    employee = baker.make(
        "nadooit_hr.Employee", user=baker.make("nadooit_auth.User", user_code="12345")
    )
    baker.make("nadooit_auth.User", user_code="123456")
    # Act
    # Assert
    assert get__employee__for__user_code("12345") == employee
    assert get__employee__for__user_code("123	") is None
    assert type(get__employee__for__user_code("123456")) == Employee


@pytest.mark.django_db
def test_create__customer_program_execution_manager_contract__for__employee_contract():
    # Arrange
    employee_contract = baker.make("nadooit_hr.EmployeeContract")
    # Act
    customer_program_execution_manager_contract = (
        create__customer_program_execution_manager_contract__for__employee_contract(
            employee_contract
        )
    )
    # Assert
    assert customer_program_execution_manager_contract.contract == employee_contract


@pytest.mark.django_db
def test_create__customer_program_execution_manager_contract__for__employee_and_customer_and_list_of_abilities_and_employee_with_customer_program_manager_contract():
    # Arrange
    employee = baker.make("nadooit_hr.Employee")
    customer = baker.make("nadooit_crm.Customer")
    abilities = [
        "can_give_manager_role",
        "can_delete_customer_program_execution",
        "can_create_customer_program_execution",
    ]
    employee_with_customer_program_manager_contract = baker.make(
        "nadooit_hr.Employee",
        user=baker.make("nadooit_auth.User", user_code="12345"),
    )
    customer_program_manager_contract = baker.make(
        "nadooit_hr.CustomerProgramExecutionManagerContract",
        contract=baker.make(
            "nadooit_hr.EmployeeContract",
            employee=employee_with_customer_program_manager_contract,
        ),
        can_create_customer_program_execution=True,
        can_delete_customer_program_execution=True,
        can_give_manager_role=True,
    )
    # Act
    customer_program_execution_manager_contract = create__customer_program_execution_manager_contract__for__employee_and_customer_and_list_of_abilities_and_employee_with_customer_program_manager_contract(
        employee, customer, abilities, employee_with_customer_program_manager_contract
    )
    # Assert
    assert customer_program_execution_manager_contract.contract.employee == employee
    assert customer_program_execution_manager_contract.contract.customer == customer
    assert (
        customer_program_execution_manager_contract.can_create_customer_program_execution
        == True
    )
    assert (
        customer_program_execution_manager_contract.can_delete_customer_program_execution
        == True
    )
    assert customer_program_execution_manager_contract.can_give_manager_role == True


@pytest.mark.django_db
def test_get__list_of_customers_the_employee_has_a_customer_program_execution_manager_contract_with_and_can_create_such_a_contract():
    # Arrange
    employee = baker.make("nadooit_hr.Employee")
    customer = baker.make("nadooit_crm.Customer", name="customer1")
    customer_program_manager_contract = baker.make(
        "nadooit_hr.CustomerProgramExecutionManagerContract",
        contract=baker.make(
            "nadooit_hr.EmployeeContract",
            employee=employee,
            customer=customer,
        ),
        can_create_customer_program_execution=True,
        can_delete_customer_program_execution=True,
        can_give_manager_role=True,
    )
    # Act

    list_of_customers_the_employee_has_a_customer_program_manager_contract_with_and_can_create_such_a_contract = get__list_of_customers_the_employee_has_a_customer_program_execution_manager_contract_with_and_can_create_such_a_contract(
        employee
    )

    print(
        list_of_customers_the_employee_has_a_customer_program_manager_contract_with_and_can_create_such_a_contract
    )

    # Assert
    assert (
        list_of_customers_the_employee_has_a_customer_program_manager_contract_with_and_can_create_such_a_contract
        == [customer]
    )


@pytest.mark.django_db
def test_get__list_of_customers_the_employee_has_a_customer_programm_manager_contract_with_and_the_customer_programms__for__employee():
    # Arrange

    """
    This is what list of customers the employee is responsible for and the customer programms looks like:
            [customer, customer_programms]

            example:
            [
                customer1, [customer_program1, customer_program2],
                customer2, [customer_program3, customer_program4],
            ]
        )
    """

    employee = baker.make("nadooit_hr.Employee")
    customer = baker.make("nadooit_crm.Customer", name="customer1")
    customer_program_manager_contract = baker.make(
        CustomerProgramManagerContract,
        contract=baker.make(
            "nadooit_hr.EmployeeContract",
            employee=employee,
            customer=customer,
        ),
        can_create_customer_program=True,
        can_delete_customer_program=True,
        can_give_manager_role=True,
    )

    customer_program = baker.make(
        CustomerProgram, customer=customer, program=baker.make(Program, name="program1")
    )

    # Act
    list_of_customers_the_employee_is_responsible_for_and_the_customer_programms = get__list_of_customers_the_employee_has_a_customer_programm_manager_contract_with_and_the_customer_programms__for__employee(
        employee
    )
    # Assert
    assert (
        list_of_customers_the_employee_is_responsible_for_and_the_customer_programms
        == [[customer, [customer_program]]]
    )


@pytest.mark.django_db
def test_get__customer_program__for__customer_program_id():
    # Arrange
    customer_program = baker.make(CustomerProgram)
    # Act
    customer_program_from_db = get__customer_program__for__customer_program_id(
        customer_program.id
    )
    # Assert
    assert customer_program_from_db == customer_program


# finish assertion
@pytest.mark.django_db
def test_get__next_price_level__for__customer_program():
    # Arrange
    customer_program = baker.make(CustomerProgram)
    # Act
    next_price_level = get__next_price_level__for__customer_program(customer_program)
    # Assert
    # test if the output is a string
    assert True


@pytest.mark.django_db
def test_get__customer_program_manager_contract__for__employee_and_customer():
    # Arrange
    # Test that returns a customer_program_manager_contract that already exists
    employee = baker.make(
        "nadooit_hr.Employee",
        user=baker.make("nadooit_auth.User", display_name="employee1"),
    )
    customer = baker.make("nadooit_crm.Customer", name="customer1")
    customer_program_manager_contract = baker.make(
        "nadooit_hr.CustomerProgramManagerContract",
        contract=baker.make(
            "nadooit_hr.EmployeeContract",
            employee=employee,
            customer=customer,
        ),
        can_create_customer_program=True,
        can_delete_customer_program=True,
        can_give_manager_role=True,
    )

    # Test that creates a new customer_program_manager_contract if it does not exist
    # There is a employee_contract between employee_2 and customer_2
    employee_2 = baker.make(
        "nadooit_hr.Employee",
        user=baker.make("nadooit_auth.User", display_name="employee2"),
    )
    customer_2 = baker.make("nadooit_crm.Customer", name="customer2")
    baker.make(
        "nadooit_hr.EmployeeContract",
        employee=employee_2,
        customer=customer_2,
    )

    # Test 3 that tests that if there is no employee_contract between employee_3 and customer_3, then it creates a new employee_contract and a new customer_program_manager_contract

    employee_3 = baker.make(
        "nadooit_hr.Employee",
        user=baker.make("nadooit_auth.User", display_name="employee3"),
    )
    customer_3 = baker.make("nadooit_crm.Customer", name="customer3")

    # Act
    customer_program_manager_contract_from_db = (
        get__customer_program_manager_contract__for__employee_and_customer(
            employee, customer
        )
    )

    customer_program_manager_contract_from_db_2 = (
        get__customer_program_manager_contract__for__employee_and_customer(
            employee_2, customer_2
        )
    )

    customer_program_manager_contract_from_db_3 = (
        get__customer_program_manager_contract__for__employee_and_customer(
            employee_3, customer_3
        )
    )

    # Assert
    assert (
        customer_program_manager_contract_from_db == customer_program_manager_contract
    )
    assert customer_program_manager_contract_from_db_2 != None
    assert customer_program_manager_contract_from_db_3 != None
    assert customer_program_manager_contract_from_db_2.contract.employee == employee_2
    assert customer_program_manager_contract_from_db_2.contract.customer == customer_2
    assert customer_program_manager_contract_from_db_3.contract.employee == employee_3
    assert customer_program_manager_contract_from_db_3.contract.customer == customer_3


@pytest.mark.django_db
def test_get__list_of_abilties__for__customer_program_manager_contract():
    # Arrange
    customer_program_manager_contract = baker.make(
        "nadooit_hr.CustomerProgramManagerContract",
        can_create_customer_program=True,
        can_delete_customer_program=True,
        can_give_manager_role=True,
    )

    customer_program_manager_contract_2 = baker.make(
        "nadooit_hr.CustomerProgramManagerContract",
        can_create_customer_program=False,
        can_delete_customer_program=False,
        can_give_manager_role=False,
    )

    customer_program_manager_contract_3 = baker.make(
        "nadooit_hr.CustomerProgramManagerContract",
        can_create_customer_program=True,
        can_delete_customer_program=False,
        can_give_manager_role=False,
    )

    customer_program_manager_contract_4 = baker.make(
        "nadooit_hr.CustomerProgramManagerContract",
        can_create_customer_program=False,
        can_delete_customer_program=True,
        can_give_manager_role=False,
    )

    customer_program_manager_contract_5 = baker.make(
        "nadooit_hr.CustomerProgramManagerContract",
        can_create_customer_program=False,
        can_delete_customer_program=False,
        can_give_manager_role=True,
    )

    # Act
    list_of_abilties_customer_program_manager_contract = (
        get__list_of_abilties__for__customer_program_manager_contract(
            customer_program_manager_contract
        )
    )

    list_of_abilties_customer_program_manager_contract_2 = (
        get__list_of_abilties__for__customer_program_manager_contract(
            customer_program_manager_contract_2
        )
    )

    list_of_abilties_customer_program_manager_contract_3 = (
        get__list_of_abilties__for__customer_program_manager_contract(
            customer_program_manager_contract_3
        )
    )

    list_of_abilties_customer_program_manager_contract_4 = (
        get__list_of_abilties__for__customer_program_manager_contract(
            customer_program_manager_contract_4
        )
    )

    list_of_abilties_customer_program_manager_contract_5 = (
        get__list_of_abilties__for__customer_program_manager_contract(
            customer_program_manager_contract_5
        )
    )

    # Assert
    assert list_of_abilties_customer_program_manager_contract == [
        "can_create_customer_program",
        "can_delete_customer_program",
        "can_give_manager_role",
    ]
    assert list_of_abilties_customer_program_manager_contract_2 == []
    assert list_of_abilties_customer_program_manager_contract_3 == [
        "can_create_customer_program",
    ]
    assert list_of_abilties_customer_program_manager_contract_4 == [
        "can_delete_customer_program",
    ]
    assert list_of_abilties_customer_program_manager_contract_5 == [
        "can_give_manager_role",
    ]


def test_get__list_of_abilities__for__list_of_selected_abilities_and_list_of_possible_abilities_the_employee_can_give():
    # Arrange
    list_of_selected_abilities = ["can_create_customer_program"]
    list_of_possible_abilities_the_employee_can_give = [
        "can_create_customer_program",
        "can_delete_customer_program",
        "can_give_manager_role",
    ]

    list_of_selected_abilities_2 = ["can_create_customer_program"]
    list_of_possible_abilities_the_employee_can_give_2 = [
        "can_delete_customer_program",
        "can_give_manager_role",
    ]

    list_of_selected_abilities_3 = ["can_create_customer_program"]
    list_of_possible_abilities_the_employee_can_give_3 = []

    list_of_selected_abilities_4 = [
        "can_create_customer_program",
        "can_delete_customer_program",
    ]
    list_of_possible_abilities_the_employee_can_give_4 = [
        "can_create_customer_program",
        "can_delete_customer_program",
        "can_give_manager_role",
    ]

    # Act
    list_of_abilities = get__list_of_abilities__for__list_of_selected_abilities_and_list_of_possible_abilities_the_employee_can_give(
        list_of_selected_abilities, list_of_possible_abilities_the_employee_can_give
    )

    list_of_abilities_2 = get__list_of_abilities__for__list_of_selected_abilities_and_list_of_possible_abilities_the_employee_can_give(
        list_of_selected_abilities_2, list_of_possible_abilities_the_employee_can_give_2
    )

    list_of_abilities_3 = get__list_of_abilities__for__list_of_selected_abilities_and_list_of_possible_abilities_the_employee_can_give(
        list_of_selected_abilities_3, list_of_possible_abilities_the_employee_can_give_3
    )

    list_of_abilities_4 = get__list_of_abilities__for__list_of_selected_abilities_and_list_of_possible_abilities_the_employee_can_give(
        list_of_selected_abilities_4, list_of_possible_abilities_the_employee_can_give_4
    )

    # Assert
    assert list_of_abilities == ["can_create_customer_program"]
    assert list_of_abilities_2 == []
    assert list_of_abilities_3 == []
    assert list_of_abilities_4 == [
        "can_create_customer_program",
        "can_delete_customer_program",
    ]


@pytest.mark.django_db
def test_set__list_of_abilities__for__customer_program_manager_contract_according_to_list_of_abilities():
    # Arrange
    customer_program_manager_contract = baker.make(
        "nadooit_hr.CustomerProgramManagerContract",
        can_create_customer_program=False,
        can_delete_customer_program=False,
        can_give_manager_role=False,
    )

    list_of_abilities = ["can_create_customer_program", "can_give_manager_role"]

    # Act
    set__list_of_abilities__for__customer_program_manager_contract_according_to_list_of_abilities(
        customer_program_manager_contract, list_of_abilities
    )

    # Assert
    assert customer_program_manager_contract.can_create_customer_program == True
    assert customer_program_manager_contract.can_delete_customer_program == False
    assert customer_program_manager_contract.can_give_manager_role == True


# TODO #130 For some reson the customers can be in the wrong order. The order is not important, but it is annoying. Fix it.
@pytest.mark.django_db
def test_get__list_of_customers_the_employee_has_a_customer_program_manager_contract_with_and_can_create_such_a_contract():
    # Arrange
    employee = baker.make("nadooit_hr.Employee")
    employee_2 = baker.make("nadooit_hr.Employee")

    customer = baker.make("nadooit_crm.Customer")
    customer_2 = baker.make("nadooit_crm.Customer")
    customer_3 = baker.make("nadooit_crm.Customer")

    # Contracts for employee

    baker.make(
        "nadooit_hr.CustomerProgramManagerContract",
        contract__employee=employee,
        contract__customer=customer,
        can_create_customer_program=True,
        can_delete_customer_program=False,
        can_give_manager_role=True,
    )

    baker.make(
        "nadooit_hr.CustomerProgramManagerContract",
        contract__employee=employee,
        contract__customer=customer_2,
        can_create_customer_program=False,
        can_delete_customer_program=False,
        can_give_manager_role=True,
    )

    baker.make(
        "nadooit_hr.CustomerProgramManagerContract",
        contract__employee=employee,
        contract__customer=customer_3,
        can_create_customer_program=False,
        can_delete_customer_program=True,
        can_give_manager_role=False,
    )

    # Contracts for employee_2

    baker.make(
        "nadooit_hr.CustomerProgramManagerContract",
        contract__employee=employee_2,
        contract__customer=customer,
        can_create_customer_program=True,
        can_delete_customer_program=False,
        can_give_manager_role=True,
    )

    baker.make(
        "nadooit_hr.CustomerProgramManagerContract",
        contract__employee=employee_2,
        contract__customer=customer_2,
        can_create_customer_program=False,
        can_delete_customer_program=False,
        can_give_manager_role=True,
    )

    # Act
    list_of_customers_the_employee_has_a_customer_program_manager_contract_with_and_can_create_such_a_contract = get__list_of_customers_the_employee_has_a_customer_program_manager_contract_with_and_can_create_such_a_contract(
        employee
    )

    # Assert
    # check that both customers are in the list but not the order
    assert (
        customer
        in list_of_customers_the_employee_has_a_customer_program_manager_contract_with_and_can_create_such_a_contract
    )
    assert (
        customer_2
        in list_of_customers_the_employee_has_a_customer_program_manager_contract_with_and_can_create_such_a_contract
    )


@pytest.mark.django_db
def test_get__list_of_customers__for__employee_manager_contract__that_can_add_employees__for__user():
    # Arrange
    employee = baker.make("nadooit_hr.Employee")
    employee_2 = baker.make("nadooit_hr.Employee")

    customer = baker.make("nadooit_crm.Customer", name="customer")
    customer_2 = baker.make("nadooit_crm.Customer", name="customer_2")

    # Contracts for employee

    baker.make(
        "nadooit_hr.EmployeeManagerContract",
        contract__employee=employee,
        contract__customer=customer,
        can_add_new_employee=True,
        can_delete_employee=False,
        can_give_manager_role=True,
    )

    baker.make(
        "nadooit_hr.EmployeeManagerContract",
        contract__employee=employee,
        contract__customer=customer_2,
        can_add_new_employee=False,
        can_delete_employee=False,
        can_give_manager_role=False,
    )

    # Contracts for employee_2

    baker.make(
        "nadooit_hr.EmployeeManagerContract",
        contract__employee=employee_2,
        contract__customer=customer,
        can_add_new_employee=True,
        can_delete_employee=False,
        can_give_manager_role=True,
    )

    baker.make(
        "nadooit_hr.EmployeeManagerContract",
        contract__employee=employee_2,
        contract__customer=customer_2,
        can_add_new_employee=True,
        can_delete_employee=False,
        can_give_manager_role=True,
    )

    # Act
    list_of_customers__for__employee_manager_contract__that_can_add_employees__for__user = get__list_of_customers__for__employee_manager_contract__that_can_add_employees__for__user(
        employee.user
    )

    list_of_customers__for__employee_manager_contract__that_can_add_employees__for__user_2 = get__list_of_customers__for__employee_manager_contract__that_can_add_employees__for__user(
        employee_2.user
    )

    # Assert
    assert (
        customer
        in list_of_customers__for__employee_manager_contract__that_can_add_employees__for__user
    )
    # assert that list_of_customers__for__employee_manager_contract__that_can_add_employees__for__user_2 is a list that contains customer and customer_2
    # but not necessarily in that order
    assert (
        customer
        in list_of_customers__for__employee_manager_contract__that_can_add_employees__for__user_2
    )
    assert (
        customer_2
        in list_of_customers__for__employee_manager_contract__that_can_add_employees__for__user_2
    )


""" 
@pytest.mark.django_db
def test_get__list_of_customers__and__their_employees__for__customers_that_have_a_employee_manager_contract__for__user():
    # Arrange
    employee = baker.make("nadooit_hr.Employee")
    employee_2 = baker.make("nadooit_hr.Employee")
    employee_3 = baker.make("nadooit_hr.Employee")

    customer = baker.make("nadooit_crm.Customer", name="customer")
    customer_2 = baker.make("nadooit_crm.Customer", name="customer_2")

    # Contracts for employee

    employee_contract_e1_c1 = baker.make(
        "nadooit_hr.EmployeeContract", employee=employee, customer=customer
    )

    baker.make(
        "nadooit_hr.EmployeeManagerContract",
        contract=employee_contract_e1_c1,
        can_add_new_employee=True,
        can_delete_employee=False,
        can_give_manager_role=True,
    )

    employee_contract_e1_c2 = baker.make(
        "nadooit_hr.EmployeeContract",
        employee=employee,
        customer=customer_2,
    )

    # Contracts for employee_2
    # employee_2 has a manager contract with customer and customer_2

    employee_contract_e2_c1 = baker.make(
        "nadooit_hr.EmployeeContract",
        employee=employee_2,
        customer=customer,
    )

    baker.make(
        "nadooit_hr.EmployeeManagerContract",
        contract=employee_contract_e2_c1,
        can_add_new_employee=True,
        can_delete_employee=False,
        can_give_manager_role=True,
    )

    employee_contract_e2_c2 = baker.make(
        "nadooit_hr.EmployeeContract",
        employee=employee_2,
        customer=customer_2,
    )

    baker.make(
        "nadooit_hr.EmployeeManagerContract",
        contract=employee_contract_e2_c2,
        can_add_new_employee=True,
        can_delete_employee=False,
        can_give_manager_role=True,
    )

    # Contracts for employee_3
    # employee_3 has a manager contract with customer_2

    employee_contract_e3_c2 = baker.make(
        "nadooit_hr.EmployeeContract",
        employee=employee_3,
        customer=customer_2,
    )

    baker.make(
        "nadooit_hr.EmployeeManagerContract",
        contract=employee_contract_e3_c2,
        can_add_new_employee=True,
        can_delete_employee=True,
        can_give_manager_role=True,
    )

    # Act
    list_of_customers__and__their_employees__for__customers_that_have_a_employee_manager_contract__for__user = get__list_of_customers__and__their_employees__for__customers_that_have_a_employee_manager_contract__for__user(
        employee.user
    )

    list_of_customers__and__their_employees__for__customers_that_have_a_employee_manager_contract__for__user_2 = get__list_of_customers__and__their_employees__for__customers_that_have_a_employee_manager_contract__for__user(
        employee_2.user
    )

    list_of_customers__and__their_employees__for__customers_that_have_a_employee_manager_contract__for__user_3 = get__list_of_customers__and__their_employees__for__customers_that_have_a_employee_manager_contract__for__user(
        employee_3.user
    )

    # Assert

    assert (
        list_of_customers__and__their_employees__for__customers_that_have_a_employee_manager_contract__for__user
        == [[customer, [employee_contract_e1_c1, employee_contract_e2_c1], False]]
    )



    assert (
        list_of_customers__and__their_employees__for__customers_that_have_a_employee_manager_contract__for__user_2
        == [
            [customer, [employee_contract_e1_c1, employee_contract_e2_c1], False],
            [
                customer_2,
                [
                    employee_contract_e1_c2,
                    employee_contract_e2_c2,
                    employee_contract_e3_c2,
                ],
                False,
            ],
        ],
    )

    assert (
        list_of_customers__and__their_employees__for__customers_that_have_a_employee_manager_contract__for__user_3
        == [
            [
                customer_2,
                [
                    employee_contract_e1_c2,
                    employee_contract_e2_c2,
                    employee_contract_e3_c2,
                ],
                True,
            ],
        ]
    )
 """


@pytest.mark.django_db
def test_check__employee_manager_contract__exists__for__employee_manager_and_customer__and__can_add_users__and__is_active():
    # Arrange
    employee = baker.make("nadooit_hr.Employee")
    customer = baker.make("nadooit_crm.Customer")

    employee_contract = baker.make(
        "nadooit_hr.EmployeeContract", employee=employee, customer=customer
    )

    baker.make(
        "nadooit_hr.EmployeeManagerContract",
        contract=employee_contract,
        can_add_new_employee=True,
        can_delete_employee=False,
        can_give_manager_role=True,
    )

    # Act
    result = check__employee_manager_contract__exists__for__employee_manager_and_customer__and__can_add_users__and__is_active(
        employee, customer
    )

    # Assert
    assert result == True


@pytest.mark.django_db
def test_get__employee_contract__for__user_code__and__customer():
    # Arrange
    employee = baker.make("nadooit_hr.Employee")
    customer = baker.make("nadooit_crm.Customer")

    employee_contract = baker.make(
        "nadooit_hr.EmployeeContract", employee=employee, customer=customer
    )

    # Act
    result = get__employee_contract__for__user_code__and__customer(
        employee.user.user_code, customer
    )

    # Assert
    assert result == employee_contract


@pytest.mark.django_db
def test_get__employee_manager_contract__for__user_code__and__customer():
    # Arrange
    employee = baker.make("nadooit_hr.Employee")
    customer = baker.make("nadooit_crm.Customer")

    employee_contract = baker.make(
        "nadooit_hr.EmployeeContract", employee=employee, customer=customer
    )

    employee_manager_contract = baker.make(
        "nadooit_hr.EmployeeManagerContract",
        contract=employee_contract,
        can_add_new_employee=True,
        can_delete_employee=False,
        can_give_manager_role=True,
    )

    # Act
    result = get__employee_manager_contract__for__user_code__and__customer(
        employee.user.user_code, customer
    )

    # Assert
    assert result == employee_manager_contract


@pytest.mark.django_db
def test_create__employee_manager_contract__for__user_code_customer_and_list_of_abilities_according_to_employee_creating_contract():
    # Arrange
    employee = baker.make("nadooit_hr.Employee")
    customer = baker.make("nadooit_crm.Customer")

    employee_contract = baker.make(
        "nadooit_hr.EmployeeContract", employee=employee, customer=customer
    )
    employee_contract_2 = baker.make("nadooit_hr.EmployeeContract", customer=customer)

    employee_manager_contract_with_all_rights: EmployeeManagerContract = baker.make(
        "nadooit_hr.EmployeeManagerContract",
        contract=employee_contract_2,
        can_add_new_employee=True,
        can_delete_employee=True,
        can_give_manager_role=True,
    )

    list_of_abilities_according_to_employee_creating_contract = [
        "can_add_new_employee",
        "can_delete_employee",
        "can_give_manager_role",
    ]

    # Act
    result = create__employee_manager_contract__for__user_code_customer_and_list_of_abilities_according_to_employee_creating_contract(
        employee.user.user_code,
        customer,
        list_of_abilities_according_to_employee_creating_contract,
        employee_manager_contract_with_all_rights.contract.employee,
    )

    # Assert
    assert type(result) == EmployeeManagerContract


@pytest.mark.django_db
def test_get__list_of_customers__for__employee_manager_contract__that_can_give_the_role__for__user():
    # Arrange
    employee = baker.make("nadooit_hr.Employee")
    customer = baker.make("nadooit_crm.Customer")

    employee_contract = baker.make(
        "nadooit_hr.EmployeeContract", employee=employee, customer=customer
    )

    employee_manager_contract = baker.make(
        "nadooit_hr.EmployeeManagerContract",
        contract=employee_contract,
        can_add_new_employee=True,
        can_delete_employee=False,
        can_give_manager_role=True,
    )

    # Act
    result = get__list_of_customers__for__employee_manager_contract__that_can_give_the_role__for__user(
        employee.user
    )

    # Assert
    assert result == [customer]


@pytest.mark.django_db
def test_set_employee_contract__as_inactive__for__employee_contract_id():
    # Arrange
    employee_contract = baker.make("nadooit_hr.EmployeeContract", is_active=True)

    # Act
    set_employee_contract__as_inactive__for__employee_contract_id(employee_contract.id)

    # Assert
    assert EmployeeContract.objects.get(id=employee_contract.id).is_active == False


@pytest.mark.django_db
def test_set__employee_contract__is_active_state__for__employee_contract_id():
    # Arrange
    employee_contract = baker.make("nadooit_hr.EmployeeContract", is_active=False)

    # Act
    set__employee_contract__is_active_state__for__employee_contract_id(
        employee_contract.id, True
    )

    # Assert
    assert EmployeeContract.objects.get(id=employee_contract.id).is_active == True


@pytest.mark.django_db
def test_get__employee_contract__for__employee_contract_id():
    # Arrange
    employee_contract = baker.make("nadooit_hr.EmployeeContract")

    # Act
    result = get__employee_contract__for__employee_contract_id(employee_contract.id)

    # Assert
    assert result == employee_contract


# TODO  #129 finish this test
@pytest.mark.django_db
def test_get__csv__for__list_of_customer_program_executions():

    # get__csv__for__list_of_customer_program_executions returns a http response with a csv file as content
    # this test checks if the content is a string
    # the content is a string because the response is a http response with a csv file as content

    # Arrange
    customer_program_execution = baker.make(
        CustomerProgramExecution,
        customer_program=baker.make(
            CustomerProgram, program=baker.make(Program, name="program_name")
        ),
    )

    # Act
    result = get__csv__for__list_of_customer_program_executions(
        [customer_program_execution]
    )

    # Assert
    assert True


@pytest.mark.django_db
def test_get__user_info__for__user():
    # Arrange
    user = baker.make("nadooit_auth.User")

    # Act
    result = get__user_info__for__user(user)

    # Assert
    assert result == {
        "user_code": user.user_code,
        "display_name": user.display_name,
    }


@pytest.mark.django_db
def test_get__list_of_manager_contracts__for__employee():

    """
    list_of_employee_contracts = [
        {
            "employee_contract": employee_contract, # the employee contract object
            "list_of_manager_contracts": [
                employee_manager_contract,
                customer_program_manager_contract,
                customer_manager_contract,
            ],
        },
        {
            "employee_contract": employee_contract, # the employee contract object
            "list_of_manager_contracts": [
                employee_manager_contract,
                customer_program_manager_contract,
                customer_manager_contract,
            ],
        },
    ]
    """

    # Arrange
    employee = baker.make(
        "nadooit_hr.Employee",
        user=baker.make("nadooit_auth.User", display_name="employee_name"),
    )

    employee_contract_1 = baker.make(
        "nadooit_hr.EmployeeContract",
        employee=employee,
        customer=baker.make("nadooit_crm.Customer", name="customer_1"),
    )

    employee_manager_contract = baker.make(
        "nadooit_hr.EmployeeManagerContract", contract=employee_contract_1
    )

    customer_program_manager_contract = baker.make(
        "nadooit_hr.CustomerProgramManagerContract",
        contract=employee_contract_1,
    )

    customer_manager_contract = baker.make(
        "nadooit_hr.CustomerManagerContract", contract=employee_contract_1
    )

    employee_contract_2 = baker.make(
        "nadooit_hr.EmployeeContract",
        employee=employee,
        customer=baker.make("nadooit_crm.Customer", name="customer_2"),
    )

    employee_manager_contract_2 = baker.make(
        "nadooit_hr.EmployeeManagerContract", contract=employee_contract_2
    )

    customer_program_manager_contract_2 = baker.make(
        "nadooit_hr.CustomerProgramManagerContract",
        contract=employee_contract_2,
    )

    employee_contract_3 = baker.make(
        "nadooit_hr.EmployeeContract",
        employee=employee,
        customer=baker.make("nadooit_crm.Customer", name="customer_3"),
    )

    # Act
    result = get__list_of_manager_contracts__for__employee(employee)

    print("result")
    print(result)

    # Assert
    assert result == [
        {
            "employee_contract": employee_contract_1,
            "list_of_manager_contracts": [
                employee_manager_contract,
                customer_program_manager_contract,
                customer_manager_contract,
            ],
        },
        {
            "employee_contract": employee_contract_2,
            "list_of_manager_contracts": [
                employee_manager_contract_2,
                customer_program_manager_contract_2,
            ],
        },
        {
            "employee_contract": employee_contract_3,
            "list_of_manager_contracts": [],
        },
    ]
