from django.shortcuts import render
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required

# Create your views here.
@login_required(login_url="/auth/login-user")
def customer_program_ownership_overview(request):
    # if the logged in user is a time account manager show the time account manager view
    return render(
        request,
        "nadooit_program_ownership_system/customer_program_ownership_overview.html",
        {
            "page_title": "Übersicht der Zeitkonten",
        },
    )


@login_required(login_url="/auth/login-user")
def admin(request):
    # if the logged in user is a time account manager show the time account manager view
    return render(
        request,
        "nadooit_program_ownership_system/customer_program_ownership_overview.html",
        {
            "page_title": "Übersicht der Zeitkonten",
        },
    )
