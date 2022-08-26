from django.shortcuts import render
#imoport for userforms

from django.contrib.auth.decorators import login_required

@login_required(login_url='/auth/login-user')
def index_nadooit_os(request):
    return render(request, 'nadooit_os/base.html')