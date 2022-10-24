from django.shortcuts import render

# imoport for userforms

from django.contrib.auth.decorators import login_required

from nadooit_time_account.models import TimeAccountManager


@login_required(login_url="/auth/login-user")
def index_nadooit_os(request):

    user_is_Time_Account_Manager = TimeAccountManager.objects.filter(
        employee__user=request.user
    ).exists()

    return render(
        request,
        "nadooit_os/index.html",
        {
            "page_title": "Nadooit OS",
            "user_is_Time_Account_Manager": user_is_Time_Account_Manager,
        },
    )
