from django.utils import timezone
from django.shortcuts import render, redirect
#imoport for userforms
from nadooit_api_executions_system.forms import ApiKeyForm
from django.http import HttpResponseRedirect

from django.contrib.auth import authenticate, login,logout
from django.contrib import messages 
from django.contrib.auth.decorators import login_required
from nadooit_api_key.models import NadooitApiKey

def login_user(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect(request.GET.get('next') or '/managment')
        else:
            messages.success(request, 'Username or Password is incorrect')
            return redirect('/managment/login_user')
    else:
       return render(request, 'authenticate/login.html', {})
   
def logout_user(request):
        logout(request)
        return redirect('/managment/login_user')




@login_required(login_url='/managment/login_user')
def index_management(request):
    return render(request, 'api_key/index_api_key_management.html')

@login_required(login_url='/managment/login_user')
def create_api_key(request):
    submitted = False
    if request.method == "POST":
        form = ApiKeyForm(request.POST)
        if form.is_valid():
            new_api_key = NadooitApiKey(api_key = form.cleaned_data['api_key'], user = form.cleaned_data['user_code'], is_active = form.cleaned_data['is_active'])
            new_api_key.updated_at = timezone.now()
            new_api_key.created_at = timezone.now()
            new_api_key.save()
            return HttpResponseRedirect('/managment/create-api-key?submitted=True')
    else:
        form = ApiKeyForm()
        if 'submitted' in request.GET:
            submitted = True
        
    form = ApiKeyForm
    return render(request, 'api_key/create_api_key.html', {'form': form, 'submitted': submitted})