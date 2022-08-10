import json
from pathlib import Path
from django.utils import timezone
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import CustomerProgram, CustomerProgramExecution, Token

# Create your views here.
#NADOOIT__API_KEY = "rtjs0t24oc(+1m6mvyd^^+*zm2=(n$#b9&#j9xxn6qi^=bj0eo"
#NADOOIT__API_KEY = os.environ.get('NADOOIT__API_KEY')

config_json = Path.home().joinpath('NADOOIT').joinpath('config').joinpath('config_dev.json')

with open(config_json) as config_file:
    config = json.load(config_file)

NADOOIT__API_KEY = config.get('NADOOIT__API_KEY')

@api_view(['POST'])
def create_execution(request):
    try:
        if request.data['NADOOIT__API_KEY'] == NADOOIT__API_KEY:
            user = Token.objects.filter(token=request.data['NADOOIT__USER_AUTH_TOKEN'],
                                        is_active=True)
            if len(user) > 0:
                obj = CustomerProgram.objects.get(id=request.data['program_id'])
                CustomerProgramExecution.objects.create(program_time_saved=obj.program_time_saved,
                                                        customer_program_id=obj)
                return Response({"status_code": 200,
                                 "msg": "created successfully"})
            else:
                return Response({"status_code": 403, "msg": "access denied user not authenticated"})
        else:
            return Response({"status_code": 403, "msg": "access denied"})

    except:
        return Response({"status_code": 500, "msg": "Internal server error"})


@api_view(['POST', 'GET'])
def token(request):
    try:
        if request.data['NADOOIT__API_KEY'] == NADOOIT__API_KEY:
            if request.method == 'GET':
                print("its a get")
                if request.data['NADOOIT__USER_AUTH_TOKEN'] != "None":
                    print("have NADOOIT__USER_AUTH_TOKEN")
                    obj = Token.objects.get(user_code=request.data['NADOOIT__USER_CODE'], token=request.data['NADOOIT__USER_AUTH_TOKEN'],
                                            is_active=True)
                    duration = timezone.now() - obj.created_at

                    days, seconds = duration.days, duration.seconds
                    hours = days * 24 + seconds // 3600
                    print(hours)
                    if days > 7:
                        obj.is_active = False
                        obj.save()
                        return Response({"status_code": 404,
                                         "msg": "no token found"})
                    else:
                        return Response({"status_code": 200,
                                         "NADOOIT__USER_CODE": obj.user_code, "token": obj.token})
                else:
                    print("have no token")
                    obj = Token.objects.get(user_code=request.data['NADOOIT__USER_CODE'],
                                            is_active=True)
                    return Response({"status_code": 200,
                                     "NADOOIT__USER_CODE": obj.user_code, "token": obj.token})
            else:
                try:
                    print(request.data)
                    obj = Token.objects.get(user_code=request.data['NADOOIT__USER_CODE'],
                                            is_active=True)
                    if obj:
                        obj.delete()
                        Token.objects.create(user_code=request.data['NADOOIT__USER_CODE'], token=request.data['NADOOIT__USER_AUTH_TOKEN'])
                    else:
                        Token.objects.create(user_code=request.data['NADOOIT__USER_CODE'], token=request.data['NADOOIT__USER_AUTH_TOKEN'])

                    return Response({"status_code": 200,
                                     "msg": "created successfully"})
                except:
                    Token.objects.create(user_code=request.data['NADOOIT__USER_CODE'], token=request.data['NADOOIT__USER_AUTH_TOKEN'])

                    return Response({"status_code": 200,
                                     "msg": "created successfully"})
        else:
            return Response({"status_code": 403, "msg": "access denied"})
    except:
        return Response({"status_code": 500, "msg": "Token not found"})


@api_view(['POST'])
def check_user(request):
    if request.data['NADOOIT__API_KEY'] == NADOOIT__API_KEY:
        obj = Token.objects.get(user_code=request.data['NADOOIT__USER_CODE'], token=request.data['NADOOIT__USER_AUTH_TOKEN'],
                                is_active=False)
        if obj:
            return True
        else:
            return False
    else:
        return Response({"status_code": 403, "msg": "access denied"})
