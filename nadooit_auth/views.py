from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required

# imoport for userforms

from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

from nadooit_auth.models import User


def log_user_in(request, username):
    user = User.objects.get(username=username)
    user.backend = "django.contrib.auth.backends.ModelBackend"
    login(request, user)
    if "redirect" in request.POST:
        return redirect(request.POST["redirect"])
    else:
        return redirect(reverse("nadooit_os:nadooit-os"))


def login_user(request):
    if request.method == "POST":
        username = request.POST["username"]
        user_code = request.POST["user_code"]
        password = request.POST["password"]

        # username = User.objects.get(user_code=user_code).username

        user = authenticate(request, username=username, password=password)

        if user is not None:
            print("found user")
            if user is not None:  # if the user object exist
                from mfa.helpers import has_mfa

                res = has_mfa(
                    username=username, request=request
                )  # has_mfa returns false or HttpResponseRedirect
                if res:
                    print("has_mfa")
                    print(res)
                    return res
                print("has_no_mfa")
                print(res)
                login(request, user)
                return redirect(request.GET.get("next") or "/nadooit-os")

        else:
            messages.success(request, "Username or Password is incorrect")
            return redirect("/auth/login-user")
    else:
        return render(request, "nadooit_auth/login.html", {})


def login_user_old(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect(request.GET.get("next") or "/nadooit-os")
        else:
            messages.success(request, "Username or Password is incorrect")
            return redirect("/auth/login-user")
    else:
        return render(request, "nadooit_auth/login.html", {})


def logout_user(request):
    logout(request)
    return redirect("/auth/login-user")


@login_required(login_url="/auth/login-user")
def register(request):
    if request.method == "POST":
        error = ""
        username = request.POST.get("username").replace("/", "")
        display_name = request.POST.get("display-name")
        if not utils.validate_username(username):
            error = "Invalid matriculation number"
            return render(
                request,
                "register.html",
                context={"page_title": "Register", "error": error},
            )
        if not utils.validate_display_name(display_name):
            error = "Invalid display name"
            return render(
                request,
                "register.html",
                context={"page_title": "Register", "error": error},
            )
        if User.objects.filter(username=username).exists():
            error = "Student already exists."
            return render(
                request,
                "register.html",
                context={"page_title": "Register", "error": error},
            )
        else:
            u = User.objects.create(
                first_name=display_name,
                password="none",
                is_superuser=False,
                username=username,
                last_name="",
                display_name=display_name,
                email="none",
                is_staff=False,
                is_active=True,
                date_joined=timezone.now(),
            )
            u.backend = "django.contrib.auth.backends.ModelBackend"
            auth.login(request, u)
            return redirect(reverse("start_fido2"))
    else:
        return render(request, "register.html", context={"page_title": "Register"})
