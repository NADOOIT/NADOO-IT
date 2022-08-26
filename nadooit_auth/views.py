from django.shortcuts import render, redirect
#imoport for userforms

from django.contrib.auth import authenticate, login,logout
from django.contrib import messages 

def login_user(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect(request.GET.get('next') or '/nadooit-os')
        else:
            messages.success(request, 'Username or Password is incorrect')
            return redirect('/auth/login-user')
    else:
       return render(request, 'authenticate/login.html', {})
   
def logout_user(request):
        logout(request)
        return redirect('/auth/login-user')