from django.shortcuts import render, redirect

# imoport for userforms

from django.contrib.auth import authenticate, login, logout
from django.contrib import messages


def login_user(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

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
