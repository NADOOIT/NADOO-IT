import json
from pathlib import Path
from django.utils import timezone
from django.shortcuts import render
#imoport for userforms
from nadooit_api_executions_system.forms import TokenForm
from django.http import HttpResponseRedirect


# Create your views here.
#NADOOIT__API_KEY = "rtjs0t24oc(+1m6mvyd^^+*zm2=(n$#b9&#j9xxn6qi^=bj0eo"
#NADOOIT__API_KEY = os.environ.get('NADOOIT__API_KEY')

#for local development
config_json = Path.home().joinpath('NADOOIT').joinpath('config').joinpath('config_dev.json')
#for production
config_json = Path.home().joinpath('NADOOIT').joinpath('config').joinpath('config.json')

with open(config_json) as config_file:
    config = json.load(config_file)

NADOOIT__API_KEY = config.get('NADOOIT__API_KEY')

def index_management(request):
    return render(request, 'token/index_token_management.html')

def create_token(request):
    submitted = False
    if request.method == "POST":
        form = TokenForm(request.POST)
        if form.is_valid():
            token = form.save(commit=False)
            token.updated_at = timezone.now()
            token.created_at = timezone.now()
            token.save()
            return HttpResponseRedirect('/token/create?submitted=True')
    else:
        form = TokenForm()
        if 'submitted' in request.GET:
            submitted = True
        
    form = TokenForm
    return render(request, 'token/create_token.html', {'form': form, 'submitted': submitted})