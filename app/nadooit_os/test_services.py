from datetime import datetime
import model_bakery
import pytest
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
def employee_with_active_TimeAccountManagerContract_and_also_managing_time_accounts_with_a_balance():
    employee = baker.make("nadooit_hr.Employee")
    for i in range(5):
        employeecontract = baker.make("nadooit_hr.EmployeeContract", employee=employee)
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
    assert (
        customer_time_accounts_grouped_by_customer_with_total_time_of_all_time_accounts
        == {<Customer: uKSbUDsNMLhePHfGHqVCaokuORKFQjnMCPQkpJwMYFHIFJuWRBZtZVirwemRoNqQtegVNuhjvpUcMZaZcSTjZpZFyfWqNpTHtpZpYOHQsUVPlYPXwnEVJSjFkipPTBWfgMoxiNKJngBqRkKeUAUrnKZJfSMrOXiFcUwGLTHVOnmkIKMlSMgyrlftaKZHDGcCGxGtGccPYLSCztxdXWUzLuDbcaovvYPzqYDIKCltbZzvvfWulwaOGqzGZGuwTyc>: {'customer_time_accounts': [<CustomerTimeAccount: uKSbUDsNMLhePHfGHqVCaokuORKFQjnMCPQkpJwMYFHIFJuWRBZtZVirwemRoNqQtegVNuhjvpUcMZaZcSTjZpZFyfWqNpTHtpZpYOHQsUVPlYPXwnEVJSjFkipPTBWfgMoxiNKJngBqRkKeUAUrnKZJfSMrOXiFcUwGLTHVOnmkIKMlSMgyrlftaKZHDGcCGxGtGccPYLSCztxdXWUzLuDbcaovvYPzqYDIKCltbZzvvfWulwaOGqzGZGuwTyc LOUmRqBxMefuiMEzrhVOwmlDZHjMhyMHWzyKzIwmIEShkRfSqICJNOtjYigbOJEodyyRzvpvobocRjNxMQavzVsWXHDajFOiwsgwCbSyMoPyLEKsDlNJBbsjdGGCcczQxpyVfiMiXZDRAbwGrlQQvceJoIOZYpEWpSEhzDlQttTtRsjoGqaTwQSltFoaekSkySQgLqWcYQfymAMyEmvshwXUDXiJEQCVgYcFqbmnCandJvVNzrxPplUiteFcAUZ 25 std : 0 min : 0 sek>, <CustomerTimeAccount: uKSbUDsNMLhePHfGHqVCaokuORKFQjnMCPQkpJwMYFHIFJuWRBZtZVirwemRoNqQtegVNuhjvpUcMZaZcSTjZpZFyfWqNpTHtpZpYOHQsUVPlYPXwnEVJSjFkipPTBWfgMoxiNKJngBqRkKeUAUrnKZJfSMrOXiFcUwGLTHVOnmkIKMlSMgyrlftaKZHDGcCGxGtGccPYLSCztxdXWUzLuDbcaovvYPzqYDIKCltbZzvvfWulwaOGqzGZGuwTyc itSwygrFiOqIuTZHlJQieDeigpmVDycETiAMaBgxwpAezUBedMaiQTjWRXCEWrrlGOsEeLadKVbVDwHDKROvgXteavKzlYTzEXEpLOBpMPqmSxgkLAkOFMrHqPfGuxZRGKgwoYmzNWKqSUCqCDrGTUBpCwNwQnYmFvwlBNGqevIgHqJHFoQvPqayOCwcWReJkhasZEXReNRditADcEPreAZfeKOqVLZRWoEbCUxWBynIHmDyaJyxQZkhyEIssMK 25 std : 0 min : 0 sek>, <CustomerTimeAccount: uKSbUDsNMLhePHfGHqVCaokuORKFQjnMCPQkpJwMYFHIFJuWRBZtZVirwemRoNqQtegVNuhjvpUcMZaZcSTjZpZFyfWqNpTHtpZpYOHQsUVPlYPXwnEVJSjFkipPTBWfgMoxiNKJngBqRkKeUAUrnKZJfSMrOXiFcUwGLTHVOnmkIKMlSMgyrlftaKZHDGcCGxGtGccPYLSCztxdXWUzLuDbcaovvYPzqYDIKCltbZzvvfWulwaOGqzGZGuwTyc snFBMWzeFJGELlzWXaJqxripPgBPCbpogGqFvxstpCAriEerbbdVPcDKohkFXWVMiWMpJmsynOKvGSCXYgDIcpKSKUTWAkvXnLcLOvpJTczyLzfkcwQEmXQAqdFKmAyMwNAKGeTuWZwYCvNWAvFjAvRIEYCLarBZlYvqMHNWedtjcSbOVhqZyIqvcFKlcdJrajnjJYNMLvsSzfiQFJfVjHjiXjsiLbOzRCOEYzMErCcVQByOuElRXATZxbyqlwY 25 std : 0 min : 0 sek>, <CustomerTimeAccount: uKSbUDsNMLhePHfGHqVCaokuORKFQjnMCPQkpJwMYFHIFJuWRBZtZVirwemRoNqQtegVNuhjvpUcMZaZcSTjZpZFyfWqNpTHtpZpYOHQsUVPlYPXwnEVJSjFkipPTBWfgMoxiNKJngBqRkKeUAUrnKZJfSMrOXiFcUwGLTHVOnmkIKMlSMgyrlftaKZHDGcCGxGtGccPYLSCztxdXWUzLuDbcaovvYPzqYDIKCltbZzvvfWulwaOGqzGZGuwTyc GKRLerBVqQsXStJsMdrawobQwPmgpnNAEHdFERmDiPAZCMRVZyPgsXUlUnUWJhbgxQfMcDugjIdUXZGxrTQCyMFyxcgZtjyxZYmHAqxPGRYSASeNIbVroXEHzhojukMTOBBMOcsbPCOLQfknQYudccAgOWAqxVngofNbRtUcbziTvGJsyTEiqxsPZfbZhsNzBlaonixvOSIsgJHjotxtQmqHKkwYrIqFuNcrdmLpOJGuGyimuIObeJGLMfUuHfZ 25 std : 0 min : 0 sek>, <CustomerTimeAccount: uKSbUDsNMLhePHfGHqVCaokuORKFQjnMCPQkpJwMYFHIFJuWRBZtZVirwemRoNqQtegVNuhjvpUcMZaZcSTjZpZFyfWqNpTHtpZpYOHQsUVPlYPXwnEVJSjFkipPTBWfgMoxiNKJngBqRkKeUAUrnKZJfSMrOXiFcUwGLTHVOnmkIKMlSMgyrlftaKZHDGcCGxGtGccPYLSCztxdXWUzLuDbcaovvYPzqYDIKCltbZzvvfWulwaOGqzGZGuwTyc kidBegwtqUmggRsvrgBNXicwyRkberyugassgKPBNVIToKaOXBlBOnJtGUpfVXArUNoNUHthVyNyIrMhZdKwlhgKBSHQGMdwfiBcUiBrweflrGYnbrvsCRDUcItoMSJLPFobDrtuUOhukIeYhKRHnEaAHifeqWSlBYGwLWVxWUbuTxRzvklWYOIftrSTzwXYRJREtBjDGflhxsOmRbVpuqyXOxcEtlEuQJARwdHRzJiXUjtNHnMFALUFVuQkVSN 25 std : 0 min : 0 sek>], 'customer_time_account_total_time_balance': '125 std : 0 min : 0 sek'}, <Customer: YFUVCameaSdfjLUsQNHzhEWMLxtsgqGgEqIHVAQOKspDmkPBpfNZnFAciZBTvoICXhKKEnFjZDwZeRtPWpZnorSAvKdFyGBgjZQnoUDPOMUohMRBRIEtLvxAompoCehllyzAQERrfaSNYfraAYrdSENBMdOQsSXrNjnZoocQrlctinhFyPISuFSCVeasWqSYlXsOpzXaFFvCoSRdISTQjydvaRPhtvwLAGOvoHyKoEJfzYBnwKrnWzaJIgYGMdP>: {'customer_time_accounts': [<CustomerTimeAccount: YFUVCameaSdfjLUsQNHzhEWMLxtsgqGgEqIHVAQOKspDmkPBpfNZnFAciZBTvoICXhKKEnFjZDwZeRtPWpZnorSAvKdFyGBgjZQnoUDPOMUohMRBRIEtLvxAompoCehllyzAQERrfaSNYfraAYrdSENBMdOQsSXrNjnZoocQrlctinhFyPISuFSCVeasWqSYlXsOpzXaFFvCoSRdISTQjydvaRPhtvwLAGOvoHyKoEJfzYBnwKrnWzaJIgYGMdP YxuelpapNNjoxylBAnXtvkPCtppSIlohpoxbddRzOBQSmDzzIfrbJUgzLduxbJLSEwYdxvuepkghmovbdpDhoUmzdHyLqFbNuOvzFzqrkRmitvaBfKcFXiuvfuwJHCSfHLfmdZeufIPPTBUJoGebdcayWYwiuLAYARVIZblEdGvVFnzhAItybmtJlJmCGvYyvtnCQtMmKLsAwCaarBdxsViBVtGMYbYPvsjcfjcwrOCDTwQxxCQVwwzYijdYIzh 25 std : 0 min : 0 sek>, <CustomerTimeAccount: YFUVCameaSdfjLUsQNHzhEWMLxtsgqGgEqIHVAQOKspDmkPBpfNZnFAciZBTvoICXhKKEnFjZDwZeRtPWpZnorSAvKdFyGBgjZQnoUDPOMUohMRBRIEtLvxAompoCehllyzAQERrfaSNYfraAYrdSENBMdOQsSXrNjnZoocQrlctinhFyPISuFSCVeasWqSYlXsOpzXaFFvCoSRdISTQjydvaRPhtvwLAGOvoHyKoEJfzYBnwKrnWzaJIgYGMdP HWuLgwNndyqLUlKzmGEIFaIPZHfTtKmmjQrEWypjBaQXWFbSyXSVszdSAOwBhfjKgmqTlvcWTVFZTbzufRCeVjsEGAgXAWqrpHkgmsROXLEfcLlfDGNzIjAXfSBMkUcGkZzLBlOsjVuoQOyTkprAxcTuOKbaRpkuKuuOMaDLQynMWZdFLikQebusgzAIQOQzWuEJFcuRVuSBuacuksDMXeemHMVUhRkZEMfshultdvxYwZzLxkPZJaNQIaOHgwg 25 std : 0 min : 0 sek>, <CustomerTimeAccount: YFUVCameaSdfjLUsQNHzhEWMLxtsgqGgEqIHVAQOKspDmkPBpfNZnFAciZBTvoICXhKKEnFjZDwZeRtPWpZnorSAvKdFyGBgjZQnoUDPOMUohMRBRIEtLvxAompoCehllyzAQERrfaSNYfraAYrdSENBMdOQsSXrNjnZoocQrlctinhFyPISuFSCVeasWqSYlXsOpzXaFFvCoSRdISTQjydvaRPhtvwLAGOvoHyKoEJfzYBnwKrnWzaJIgYGMdP EMgFMMpAYoSgfhAPaMnFlqgiQeQWRxtXdCHpuhLVmxpLjlGrLsBrOifrxMpPylJrFdOZRxGTNsMSDdNqwnSjHNdejAaFnmjVTcVMoizhKzHxsIqUYflVOqhqYnkTmKcFyCtmyViOksONhPXpgQHYGakHtcdHdWVgxjEIPFjCokCKPPIFDuCxlfkbzwLxybESwCVZBtSuzAENRETSPULqXjMYVZZUqlKsqNfjVuaNxOzLmpNcGkIbnjyhHVysWKs 25 std : 0 min : 0 sek>, <CustomerTimeAccount: YFUVCameaSdfjLUsQNHzhEWMLxtsgqGgEqIHVAQOKspDmkPBpfNZnFAciZBTvoICXhKKEnFjZDwZeRtPWpZnorSAvKdFyGBgjZQnoUDPOMUohMRBRIEtLvxAompoCehllyzAQERrfaSNYfraAYrdSENBMdOQsSXrNjnZoocQrlctinhFyPISuFSCVeasWqSYlXsOpzXaFFvCoSRdISTQjydvaRPhtvwLAGOvoHyKoEJfzYBnwKrnWzaJIgYGMdP CaFRVWLfRlvUiaRQeSJwAZcJTRWFAkYjwSkwOpqWldRKlaxnVZtEjCKCNAOpQiyiOzeenfgATObpFkgXWghtdgECpDSTuVDulViszxxpFSmopNgikderyfYjEZqGacEefyyVDkbtseQoJPzvNJJHtobANEnlAptcMeMFJCnhhzIBTpoYRzyRlCCpwmqnjbDbhVoSATFRydrkABdYfTFqucwXzUtNdNItmNDZfszvYWAYfdckENRGwjDAKcqUKzQ 25 std : 0 min : 0 sek>, <CustomerTimeAccount: YFUVCameaSdfjLUsQNHzhEWMLxtsgqGgEqIHVAQOKspDmkPBpfNZnFAciZBTvoICXhKKEnFjZDwZeRtPWpZnorSAvKdFyGBgjZQnoUDPOMUohMRBRIEtLvxAompoCehllyzAQERrfaSNYfraAYrdSENBMdOQsSXrNjnZoocQrlctinhFyPISuFSCVeasWqSYlXsOpzXaFFvCoSRdISTQjydvaRPhtvwLAGOvoHyKoEJfzYBnwKrnWzaJIgYGMdP HYCjXYrgTkhjCAMWyQOFNYfSssriCTftiJdXPtBCpCPUPPSmQVbfqkgEwByRlDaXogWrJKIgGMwVCZYhEHHdvlsFiSpcMSZpbQFSVdZyHBPxGALryosZSNYsYohJvAmnvhMVupXUHKqvxFmvAsbiNZgCuMewCJFscVCqvVPTWbofHyWGopjAGGxmfotXTNFSdIaSkMBWeZiogxfaMmHhXVbITgYQyVnwpaNJVLdCqLOEjAoqjnIJAtEMuUetAPp 25 std : 0 min : 0 sek>], 'customer_time_account_total_time_balance': '125 std : 0 min : 0 sek'}, <Customer: QbbcmWhsMoTTiPckpMMqRANuQclrCEpjEaviwQiEtzGRciLvsHahzYVMbDWBFlmJiKByZHkAExSzLAWXbCuGIhrSelyCckFwxdxYlXrGvErawPrxXjDYRtcvTRGVDSwMIjCJyXGHlyXadHdFPSZyoIXqhuNLtWpeIDMCOBWiKmioKmjlgHPdeqeUShTBgOGzWSyilOJzJuQaOlJAQyDvVDtzyTKdEQBZbzoFMlfDYcgGMjBLMUzWuVUjACiCOJr>: {'customer_time_accounts': [<CustomerTimeAccount: QbbcmWhsMoTTiPckpMMqRANuQclrCEpjEaviwQiEtzGRciLvsHahzYVMbDWBFlmJiKByZHkAExSzLAWXbCuGIhrSelyCckFwxdxYlXrGvErawPrxXjDYRtcvTRGVDSwMIjCJyXGHlyXadHdFPSZyoIXqhuNLtWpeIDMCOBWiKmioKmjlgHPdeqeUShTBgOGzWSyilOJzJuQaOlJAQyDvVDtzyTKdEQBZbzoFMlfDYcgGMjBLMUzWuVUjACiCOJr VMdbGhcNPBJRCoEpgoNrREYdFiftAbdvgdUNpRtPATPzMdibMrjBlDHWdCpWZMdTGBQOJzbGAZlcYcUWWrZYmPdVYIdzDeOEqaLMYyByVUNdgQLQgndWWkuJSWfxENoEyKgbZLEpkdimgUNuRsktWdTLeitWycpVlCKPbVPzUfvzILYUsYVECHjZYlviUYGLsXCumDdqLLpKflWYQiLfQRhqeHZfgIZcAyKxJfHRYwTQoTxRxgyKmmKgrllQGoN 25 std : 0 min : 0 sek>, <CustomerTimeAccount: QbbcmWhsMoTTiPckpMMqRANuQclrCEpjEaviwQiEtzGRciLvsHahzYVMbDWBFlmJiKByZHkAExSzLAWXbCuGIhrSelyCckFwxdxYlXrGvErawPrxXjDYRtcvTRGVDSwMIjCJyXGHlyXadHdFPSZyoIXqhuNLtWpeIDMCOBWiKmioKmjlgHPdeqeUShTBgOGzWSyilOJzJuQaOlJAQyDvVDtzyTKdEQBZbzoFMlfDYcgGMjBLMUzWuVUjACiCOJr flTKhZHKOipdpRXNkicVeHhHJjKtwoSYUAYFmvxaoIgHMtneSFPfaAFfioNMcRZMXozNFhVqSenymrzkUWfOOqEEwZvzEkeblWlTcamdAAsHXsXNLdlaXcbmtFFNRCpReHbQnPBSBcCGRHCgkxDtVaUPGEhuVgldMUzkTZJKUjcFkMIBySaCUNghyxOaUEEnEjEaWmCQYkGbDqzXPkpBUICsUqPSKyHuceGSxffWzaQdLjjerplYeSEZSfPusXx 25 std : 0 min : 0 sek>, <CustomerTimeAccount: QbbcmWhsMoTTiPckpMMqRANuQclrCEpjEaviwQiEtzGRciLvsHahzYVMbDWBFlmJiKByZHkAExSzLAWXbCuGIhrSelyCckFwxdxYlXrGvErawPrxXjDYRtcvTRGVDSwMIjCJyXGHlyXadHdFPSZyoIXqhuNLtWpeIDMCOBWiKmioKmjlgHPdeqeUShTBgOGzWSyilOJzJuQaOlJAQyDvVDtzyTKdEQBZbzoFMlfDYcgGMjBLMUzWuVUjACiCOJr vcANkQeXNhMnXVNSuOLSCdVVICxtktXhDaJLaQdODHCloewoozaBBNMObgglcbfUuOjmNRqzMjidnwejOqBtyxAwcMPmbUsjLhFPhpSbmWcSGkpLEpxUbdYfZNICDXUhcoQerCvlTKSGGsghuqRZAmLCdWiTkRycsBiErYDxyURLGsIHfeoIwilGOFCFsNvCVxYBUoWgizVsuYgFIhYsamhkXIPsagjVPRFfNqvsuyuxcdtrNUdBZLYcuKdVDnN 25 std : 0 min : 0 sek>, <CustomerTimeAccount: QbbcmWhsMoTTiPckpMMqRANuQclrCEpjEaviwQiEtzGRciLvsHahzYVMbDWBFlmJiKByZHkAExSzLAWXbCuGIhrSelyCckFwxdxYlXrGvErawPrxXjDYRtcvTRGVDSwMIjCJyXGHlyXadHdFPSZyoIXqhuNLtWpeIDMCOBWiKmioKmjlgHPdeqeUShTBgOGzWSyilOJzJuQaOlJAQyDvVDtzyTKdEQBZbzoFMlfDYcgGMjBLMUzWuVUjACiCOJr nSMwekLTgmUzBrnAULaROwJBHzLedXrEFaRXkPiUbyjqESNSyEusvjpBCKaYCCJekQrpzXJGNmmpbNThljQwUvbiIWENePbuUHOuSqJxbeWlxgydcKDHUqUtPDOCiNJErtoGwQGLsWpbOomojEHFRXwRjLgBowbXLpRmEdkpvmJWiTZhsfnwgIyHlQqhuVzBWIpmJDsAmAPiJSEkBpeWfFbvXvVpMSVhTLgSGGxVBcOnLwQksAwzZtBsKueQaFy 25 std : 0 min : 0 sek>, <CustomerTimeAccount: QbbcmWhsMoTTiPckpMMqRANuQclrCEpjEaviwQiEtzGRciLvsHahzYVMbDWBFlmJiKByZHkAExSzLAWXbCuGIhrSelyCckFwxdxYlXrGvErawPrxXjDYRtcvTRGVDSwMIjCJyXGHlyXadHdFPSZyoIXqhuNLtWpeIDMCOBWiKmioKmjlgHPdeqeUShTBgOGzWSyilOJzJuQaOlJAQyDvVDtzyTKdEQBZbzoFMlfDYcgGMjBLMUzWuVUjACiCOJr ZiqcAwvXLslnhQaqcXJyZjXJkavIbbtdPzGiFGmUXtTvGGmbSVeQHRvOTPJenMFzaPdVfQyfEzxtsXVxuSEPqNehwfdFeCIkRjLZZdZWEBHkcwRyYLaQhUXoYXJQPYSjrLxDeiIUsWyVmKSOWgyJsyssPyZbvHTsAbgZMfcssrMDkUTcjOwsTUrdglgtOuIOftcuTIWsjgVtQJFMAScJadhCMHPibojXPljspGbAkPfkmNAMpfzGaufRRuKYGTq 25 std : 0 min : 0 sek>], 'customer_time_account_total_time_balance': '125 std : 0 min : 0 sek'}, <Customer: mZzSYpHTKHGJozAIpuYNoWohUKoBrhCDLNIJcKLPdgNBlqokCgOTJIjlstNDsBmbrPzeheATsHkcqUyIsjQGqFlUmCkSsJByjQJlsIUudoCTwPRxZpFWnLjnTVQyfFUCKwJacurOejZwkbQfNGlYRuHfgMzEBfOXqlXkRPNiKclnWiMWpXdnFGLuDgHscCpweuLNlobeHRRYRljqwwLfNcLaTxtzUsiCttTaNojnzZVWMaDupBeoXnQgTvJZTHa>: {'customer_time_accounts': [<CustomerTimeAccount: mZzSYpHTKHGJozAIpuYNoWohUKoBrhCDLNIJcKLPdgNBlqokCgOTJIjlstNDsBmbrPzeheATsHkcqUyIsjQGqFlUmCkSsJByjQJlsIUudoCTwPRxZpFWnLjnTVQyfFUCKwJacurOejZwkbQfNGlYRuHfgMzEBfOXqlXkRPNiKclnWiMWpXdnFGLuDgHscCpweuLNlobeHRRYRljqwwLfNcLaTxtzUsiCttTaNojnzZVWMaDupBeoXnQgTvJZTHa PxiHufaFVDkTrkaDXlGePRtfdvUrXwARUQCpthiVENMDeQCppcZmRMvSQTwCrfXgzcWhIZWIMNnDqNRLUHwAXbnIwbARQmmeYpUUWRlScLOiKQscvNimLDJkndTmPsRqxdEvCThenkSFFAjWdQnpVAChnYBrioFjHsuHKLsHnhrNBNknXEFKbtpfvASYjCuMXSIUXomVREIBTDdkbAfoSWEcnALyaqqeRtJRhYTdwRHfiQLyGVfuqOGTnjyzTeu 25 std : 0 min : 0 sek>, <CustomerTimeAccount: mZzSYpHTKHGJozAIpuYNoWohUKoBrhCDLNIJcKLPdgNBlqokCgOTJIjlstNDsBmbrPzeheATsHkcqUyIsjQGqFlUmCkSsJByjQJlsIUudoCTwPRxZpFWnLjnTVQyfFUCKwJacurOejZwkbQfNGlYRuHfgMzEBfOXqlXkRPNiKclnWiMWpXdnFGLuDgHscCpweuLNlobeHRRYRljqwwLfNcLaTxtzUsiCttTaNojnzZVWMaDupBeoXnQgTvJZTHa GpqzTWTSigQNLYLyMxSpjgpZYkguXiYIlyiplwhbWEGHeWstBotMfzmEAxyZwLEekdUHAhNXuCiFOVeZxOXAfNsnWqjEjZCxMKXNjbJcDUHEDKGrwPcKMNcwjRomiZRPOmJHIJNkmvudBgFHvvqjdfNIIVuxAjfXpzIfxwythlbdTzNMfNERmXkBhKXcnNFHmySzlXHtUAzHeDLdlDAlbNhFGmAbipTsqRauHFBSQqijvxrKnQyiKOUUbvCxpbd 25 std : 0 min : 0 sek>, <CustomerTimeAccount: mZzSYpHTKHGJozAIpuYNoWohUKoBrhCDLNIJcKLPdgNBlqokCgOTJIjlstNDsBmbrPzeheATsHkcqUyIsjQGqFlUmCkSsJByjQJlsIUudoCTwPRxZpFWnLjnTVQyfFUCKwJacurOejZwkbQfNGlYRuHfgMzEBfOXqlXkRPNiKclnWiMWpXdnFGLuDgHscCpweuLNlobeHRRYRljqwwLfNcLaTxtzUsiCttTaNojnzZVWMaDupBeoXnQgTvJZTHa QtPKFWFtwIxizHCnWnzLBPPeKMvSNwBblLslcemiDTJqyfmGauHoVERTnEbBkBkbtRvSaUtoSfZFzUFSGOuCdTzPLRjzbAXZAhktCizIeGBUwrpqjdGpJhNggZUtsyPecgEYtXlMugflFLGZsvqYswRhrLSCvmgoUzOuoXiXlxtUBBVDgOhJXzkRJHbTdtgQTHCmHOnODatXPTzmYDFArRBTCQNRnmQbwmkRWOYAhvhnwHbpIskjfchCiVWmPzD 25 std : 0 min : 0 sek>, <CustomerTimeAccount: mZzSYpHTKHGJozAIpuYNoWohUKoBrhCDLNIJcKLPdgNBlqokCgOTJIjlstNDsBmbrPzeheATsHkcqUyIsjQGqFlUmCkSsJByjQJlsIUudoCTwPRxZpFWnLjnTVQyfFUCKwJacurOejZwkbQfNGlYRuHfgMzEBfOXqlXkRPNiKclnWiMWpXdnFGLuDgHscCpweuLNlobeHRRYRljqwwLfNcLaTxtzUsiCttTaNojnzZVWMaDupBeoXnQgTvJZTHa TJTtaswKIWkNRDzMPiwoKUbWcfNIrXzQfQjfreImxNbyxvTFAhYyvMTbQHQFfhLxmuPCOVyPerXmuvqgtkuYNbXrUnsJieuExjdnPnRQyhgJmUmLMgDkUHwoTPyHBmUcwOXyJCcoDjgDsreXDCcckeaxmwZkRqEhsyNiUNhgygEdouFetqPmtiBbafFAtOOGzwGqzXUWBSKxSBqYOerHtPeaadeQLTgeJmsocqfWCkBijSVJTglyGBpqclepmwj 25 std : 0 min : 0 sek>, <CustomerTimeAccount: mZzSYpHTKHGJozAIpuYNoWohUKoBrhCDLNIJcKLPdgNBlqokCgOTJIjlstNDsBmbrPzeheATsHkcqUyIsjQGqFlUmCkSsJByjQJlsIUudoCTwPRxZpFWnLjnTVQyfFUCKwJacurOejZwkbQfNGlYRuHfgMzEBfOXqlXkRPNiKclnWiMWpXdnFGLuDgHscCpweuLNlobeHRRYRljqwwLfNcLaTxtzUsiCttTaNojnzZVWMaDupBeoXnQgTvJZTHa aVeHoJwgFrcqWmsxCjxxNWvnEyRwrMdhKasYdhZDNYNfCEzwHLWXxyxgDoUWdqIHfaegsZottaHnoXCMmmUdyjTxKTYvHnizCUjJUTXuvBckNdvGiFxTZvhUjVpnSEQXDhPbIQRWXMNeMHEZtVaBnIPCzqLNaJKolNEEyYGvhZuSVEHTPUBysYcyQDijeCbTOxncYkflJUZtLpqqFGDlKWSsJIUUBiiTRGTYokWKKHsdzoTmiBAYNqpaXaQgAuo 25 std : 0 min : 0 sek>], 'customer_time_account_total_time_balance': '125 std : 0 min : 0 sek'}, <Customer: WSfdXvozfdOKEUfvLUTiSdwLIdyKdxVzxxrllVGeTjBaZEYIbGDslnUmSOwIMNgPODRsWinqUPBQtxBKjStNvAYWOEyzgbskfjVhUczguGWVxTozYbRRYMaxVYipOAcchkAMDWrOJYwhmhzYlqrXbqAltpGUHxNfjdjAcUBlFqmdmizTjZwuFRfQVUNsduiRnmcLbBGrKspMOzqtkWTZMzvXTkPoBwkghxCTFRDUqryoTPftAVQFMfPFGRQNGBv>: {'customer_time_accounts': [<CustomerTimeAccount: WSfdXvozfdOKEUfvLUTiSdwLIdyKdxVzxxrllVGeTjBaZEYIbGDslnUmSOwIMNgPODRsWinqUPBQtxBKjStNvAYWOEyzgbskfjVhUczguGWVxTozYbRRYMaxVYipOAcchkAMDWrOJYwhmhzYlqrXbqAltpGUHxNfjdjAcUBlFqmdmizTjZwuFRfQVUNsduiRnmcLbBGrKspMOzqtkWTZMzvXTkPoBwkghxCTFRDUqryoTPftAVQFMfPFGRQNGBv xsDvcJiICBjsHqlrYKIKCeQpKJUogNJfZRuHVNVlDpBeYlMiXOojpjhDVfJBkygfNEwYtcHMIsIzMjIeKgZNGclLiCEicrnfiCUHxUgORPlbofnSczNGCEszpkOlIWcZajCWqYSxmuteybgUwcoXCgkpiMJfUBpxAoDklkmhnygsqYTgezTsFEzytAnKRNWEGZRQKHhJFGHtWUhJbFxPgjAYWxZqDFckdpMfBJFepNPLAcnWtQYNupIOlmRYWvS 25 std : 0 min : 0 sek>, <CustomerTimeAccount: WSfdXvozfdOKEUfvLUTiSdwLIdyKdxVzxxrllVGeTjBaZEYIbGDslnUmSOwIMNgPODRsWinqUPBQtxBKjStNvAYWOEyzgbskfjVhUczguGWVxTozYbRRYMaxVYipOAcchkAMDWrOJYwhmhzYlqrXbqAltpGUHxNfjdjAcUBlFqmdmizTjZwuFRfQVUNsduiRnmcLbBGrKspMOzqtkWTZMzvXTkPoBwkghxCTFRDUqryoTPftAVQFMfPFGRQNGBv rsEgBtPESjuKLJjZmOkAlCxfyddyYUqquAJITnWXkwHQuSjCpZMgVrTMAOhYWMNVJXHkvrWAxFQpDlEkIdvafWtNUcgGquidynpyjTduFwjrfaFaNumgJPiIuCzlOSEPRHHIRTMsaSQSvFJWCszNHXcEDxVvSqSEzpqvrljOGWmSRsHmcLuQhZYVtRvjaoMfuopLpHSnsplamoLcuttXWdLQySZDTZVbqWFgZXByzRPWfEyYliIACDceetEiOmO 25 std : 0 min : 0 sek>, <CustomerTimeAccount: WSfdXvozfdOKEUfvLUTiSdwLIdyKdxVzxxrllVGeTjBaZEYIbGDslnUmSOwIMNgPODRsWinqUPBQtxBKjStNvAYWOEyzgbskfjVhUczguGWVxTozYbRRYMaxVYipOAcchkAMDWrOJYwhmhzYlqrXbqAltpGUHxNfjdjAcUBlFqmdmizTjZwuFRfQVUNsduiRnmcLbBGrKspMOzqtkWTZMzvXTkPoBwkghxCTFRDUqryoTPftAVQFMfPFGRQNGBv URrJRFtPBKIiKlYioIhnzfSyEUvhivzIwqfwQHyqsgmxHnWpJxNkIiLHduyxIKupqfrSHrkUKBdfwUMixygNyzRmAZxOTpWKwbLFRRmJWEaqbosHDJKjbbQqrrVugBzfvSUbpWMjJWhVapIepGuIvcStzxUJkQioAJpTQXFolzeZtRaetYnzVxkAXiVhrTfIFYaWWwCrghoKnSeLJrhoJswWGlBQyNgzNKPhsZzPwLdmDjpWgGXIbhxebMTArJt 25 std : 0 min : 0 sek>, <CustomerTimeAccount: WSfdXvozfdOKEUfvLUTiSdwLIdyKdxVzxxrllVGeTjBaZEYIbGDslnUmSOwIMNgPODRsWinqUPBQtxBKjStNvAYWOEyzgbskfjVhUczguGWVxTozYbRRYMaxVYipOAcchkAMDWrOJYwhmhzYlqrXbqAltpGUHxNfjdjAcUBlFqmdmizTjZwuFRfQVUNsduiRnmcLbBGrKspMOzqtkWTZMzvXTkPoBwkghxCTFRDUqryoTPftAVQFMfPFGRQNGBv UyqZueqagNkFHJbFBdbBGoKeVaiMbziljSOjocTcQfJjWHBnVQSeOQqiWkliamKMxwEOmRqurbyXJVkckBnYauSngBSsFKRGycIeMKPQhrDbtOBzAXcGswxZGtElXmubaATRNxMxbSdkozHDGDeYJbhvGOyczGqyBQGulBNHmpTjFVgabAqUjuGCzbIwMovhkphzEJcYGFNPLrVbcgdwSadpNHIWtFmwngXNFNIBOjGteMhwgzRMRrwpNOsTyZk 25 std : 0 min : 0 sek>, <CustomerTimeAccount: WSfdXvozfdOKEUfvLUTiSdwLIdyKdxVzxxrllVGeTjBaZEYIbGDslnUmSOwIMNgPODRsWinqUPBQtxBKjStNvAYWOEyzgbskfjVhUczguGWVxTozYbRRYMaxVYipOAcchkAMDWrOJYwhmhzYlqrXbqAltpGUHxNfjdjAcUBlFqmdmizTjZwuFRfQVUNsduiRnmcLbBGrKspMOzqtkWTZMzvXTkPoBwkghxCTFRDUqryoTPftAVQFMfPFGRQNGBv joFtnwAvLEuAWrqZsFbYJfpHAcIEEBqNbyTwRqFhzwXIPbYmXcDzlSubGzXuUotJsWhjYwVVCeGqJRpxSFikAJYQnqIwfFUzCeYFAokfMOVVRKAFNfnqzwrWBKYaYNRSVKtAFCDxteFGUoaUPONnwnAYngsNJwfGqiXesPyxuzZwibvfBcjkBsQebkJVWjaBVDRkcsgnDuRjbzFhIfSZdklORjxYnrGhaCOttJtvraDmCnTOdtrwsCfInHYEjvV 25 std : 0 min : 0 sek>], 'customer_time_account_total_time_balance': '125 std : 0 min : 0 sek'}}
    )
