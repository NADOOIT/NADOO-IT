from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from nadooit_time_account.models import (
    get_time_as_string_in_hour_format_for_time_in_seconds_as_integer,
)
from nadooit_hr.models import Employee
from nadooit_time_account.models import TimeAccountManager
from nadooit_time_account.logic import (
    get__total_of_all_customer_time_account_balances__for__user,
)


# Create your views here.
@login_required(login_url="/auth/login-user")
def customer_time_account_overview(request):
    # if the logged in user is a time account manager show the time account manager view
    current_balance = get__total_of_all_customer_time_account_balances__for__user(
        request.user
    )
    print(current_balance)

    time_accounts_the_user_is_responsible_for = TimeAccountManager.objects.get(
        employee=Employee.objects.get(user=request.user)
    ).time_accounts.all()
    list_of_time_accounts_formatted = []
    for time_account in time_accounts_the_user_is_responsible_for:

        list_of_time_accounts_formatted.append(
            {
                "id": time_account.id,
                "name": time_account.name,
                "time_balance": get_time_as_string_in_hour_format_for_time_in_seconds_as_integer(
                    time_account.time_balance_in_seconds
                ),
            },
        )
    return render(
        request,
        "nadooit_time_account/customer_time_account_overview.html",
        {
            "page_title": "Übersicht der Zeitkonten",
            "current_balance": current_balance,
            "time_accounts_the_user_is_responsible_for": list_of_time_accounts_formatted,
        },
    )


@login_required(login_url="/auth/login-user")
def customer_order_overview(request):

    # All orders for the current customer

    # Multiple lists for the different order states
    # List one shows all orders for the current month
    # List shows all previous orders

    return render(
        request,
        "nadooit_time_account/customer_time_account_overview.html",
        {
            "page_title": "Übersicht der Buchungen",
            "current_balance": current_balance,
            "time_accounts_the_user_is_responsible_for": time_accounts_the_user_is_responsible_for,
        },
    )


@login_required(login_url="/auth/login-user")
def admin(request):
    return render(
        request,
        "nadooit_time_account/admin.html",
        {"page_title": "Übersicht der Zeitkonten"},
    )
