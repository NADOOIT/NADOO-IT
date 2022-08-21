import json
from pathlib import Path
from django.utils import timezone
from django.shortcuts import render
#imoport for userforms
from nadooit_api_executions_system.forms import ApiKeyForm
from django.http import HttpResponseRedirect

from nadooit_api_executions_system.models import NadooitApiKey


def index_management(request):
    return render(request, 'api_key/index_api_key_management.html')

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