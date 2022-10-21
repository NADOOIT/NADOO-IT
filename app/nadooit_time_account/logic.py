from nadooit_hr.models import Employee
from nadooit_time_account.models import (
    TimeAccountManager,
    get_time_as_string_in_hour_format_for_time_in_seconds_as_integer,
)


def get__total_of_all_customer_time_account_balances__for__user(User):
    if Employee.objects.filter(user=User).exists():
        print("Employee exists")
        print(Employee.objects.get(user=User))
        time_accounts_the_user_is_responsible_for = TimeAccountManager.objects.get(
            employee=Employee.objects.get(user=User)
        ).time_accounts.all()
        total_of_all_customer_time_account_balances = 0
        print(time_accounts_the_user_is_responsible_for)
        for time_account in time_accounts_the_user_is_responsible_for:
            total_of_all_customer_time_account_balances += (
                time_account.time_balance_in_seconds
            )
        return get_time_as_string_in_hour_format_for_time_in_seconds_as_integer(
            total_of_all_customer_time_account_balances
        )
    else:
        return "0:0:0"
