from django.utils import timezone
from django.shortcuts import render
#imoport for userforms

from django.http import HttpResponseRedirect

from django.contrib.auth.decorators import login_required
from nadooit_api_key.forms import ApiKeyForm
from nadooit_api_key.models import NadooitApiKey


@login_required(login_url='/auth/login-user')
def api_key_interface(request):
    return render(request, 'api_key_base.html')


@login_required(login_url='/auth/login-user')
def create_api_key(request):
    submitted = False
    if request.method == "POST":
        form = ApiKeyForm(request.POST)
        if form.is_valid():
            new_api_key = NadooitApiKey(api_key = form.cleaned_data['api_key'], user = form.cleaned_data['user_code'], is_active = form.cleaned_data['is_active'])
            new_api_key.updated_at = timezone.now()
            new_api_key.created_at = timezone.now()
            new_api_key.save()
            return HttpResponseRedirect('/nadooit-api-key/create-api-key?submitted=True')
    else:
        form = ApiKeyForm()
        if 'submitted' in request.GET:
            submitted = True
        
    form = ApiKeyForm
    return render(request, 'create_api_key.html', {'form': form, 'submitted': submitted})