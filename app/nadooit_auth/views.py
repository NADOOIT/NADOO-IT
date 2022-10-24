import django.contrib.auth.validators
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test


from app.nadooit.settings import DEBUG
from .user_code import get__new_user_code


from nadooit_auth.models import User
from nadooit_auth.user_code import check__valid_user_code
from nadooit_auth.username import get__new_username


def user_is_KeyManager_that_can_create_new_keys(user):
    if hasattr(user.employee, "keymanager"):
        return user.employee.keymanager.can_create_keys
    return False


def log_user_in(request, username):
    user = User.objects.get(username=username)
    user.backend = "django.contrib.auth.backends.ModelBackend"

    # loging in the user
    login(request, user)
    # request.POST containing redirect might be wrong here and should be request.GET "next" instead. Test this.
    if "redirect" in request.POST:
        return redirect(request.POST["redirect"])
    else:
        return redirect(reverse("nadooit_os:nadooit-os"))


def login_user(request):
    if request.method == "POST":
        # username = request.POST["username"]
        user_code = request.POST["user_code"]
        # password = request.POST["password"]

        # OLD user = authenticate(request, username=username)
        user = authenticate(request, user_code=user_code)
        print("user: ", user)
        err = ""
        if user is not None:
            print("found user")
            if user.is_active:  # if the user object exist
                if "mfa" in settings.INSTALLED_APPS and settings.DEBUG == False:
                    from mfa.helpers import has_mfa

                    res = has_mfa(
                        username=user.username, request=request
                    )  # has_mfa returns false or HttpResponseRedirect
                    if res:
                        print("has_mfa")
                        print(res)
                        return res
                    print("has_no_mfa")
                    print(res)
                    log_user_in(request, user.username)
                    # login(request, user)
                    return redirect(request.GET.get("next") or "/nadooit-os")
                else:
                    pass
            else:
                err = "This user is NOT activated yet."
        else:
            err = "Username or Password is incorrect"
        messages.success(request, err)
        return redirect("/auth/login-user")

    else:
        return render(request, "nadooit_auth/login.html", {})


def logout_user(request):
    logout(request)
    messages.success(request, "You habe successfully logged out")
    return redirect("/auth/login-user")


@login_required(login_url="/auth/login-user")
@user_passes_test(
    user_is_KeyManager_that_can_create_new_keys,
    redirect_field_name=None,
    login_url="/nadooit-os",
)
def register_user(request):
    if request.method == "POST":
        error = ""
        user_code = request.POST.get("user_code").replace("/", "")
        display_name = request.POST.get("display_name")
        if not check__valid_user_code(user_code):
            error = "Invalid user_code"
            return render(
                request,
                "nadooit_auth/register.html",
                context={"page_title": "Register", "error": error},
            )
        if User.objects.filter(user_code=user_code).exists():
            error = "user_code already exists."
            return render(
                request,
                "nadooit_auth/register.html",
                context={"page_title": "Register", "error": error},
            )
        else:
            username = get__new_username()
            first_name = get__new_username()
            u = User.objects.create(
                first_name=first_name,
                password="none",
                is_superuser=False,
                username=username,
                user_code=user_code,
                last_name="",
                display_name=display_name,
                email="none",
                is_staff=False,
                is_active=True,
                date_joined=timezone.now(),
            )
            u.backend = "django.contrib.auth.backends.ModelBackend"
            login(request, u)
            return redirect(reverse("start_fido2"))
    else:
        return render(
            request,
            "nadooit_auth/register.html",
            context={"page_title": "Register", "user_code": get__new_user_code()},
        )
