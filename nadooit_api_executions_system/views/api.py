import hashlib
from rest_framework.decorators import api_view
from rest_framework.response import Response
from nadooit_api_executions_system.models import CustomerProgram, CustomerProgramExecution, NadooitApiKey, User

# Create your views here.

@api_view(['POST'])
def create_execution(request):
    try:
        hashed_api_key = hashlib.sha256(request.data.get('NADOOIT__API_KEY').encode()).hexdigest()
        try:
            found_nadooit_api_key = NadooitApiKey.objects.get(api_key=hashed_api_key, is_active = True)
           
            if found_nadooit_api_key.user.user_code != request.data.get('NADOOIT__USER_CODE'):
                return Response({"error": "User code is not valid"}, status=400)
            
            if found_nadooit_api_key.user.user_code != request.data.get('NADOOIT__USER_CODE') and not found_nadooit_api_key.user.is_active:
                return Response({"error": "User is not active"}, status=400)
            else:
                obj = CustomerProgram.objects.get(id=request.data['program_id'])
                CustomerProgramExecution.objects.create(program_time_saved=obj.program_time_saved,
                                                        customer_program_id=obj)
                return Response({"success": "Execution created"}, status=200)     
        except NadooitApiKey.DoesNotExist:	    
            return Response({"error": "Invalid API Key"}, status=401)
    except:
        return Response({"error": "Invalid request"}, status=400)

@api_view(['POST'])
def check_user(request):
    try:
        hashed_api_key = hashlib.sha256(request.data.get('NADOOIT__API_KEY').encode()).hexdigest()
        try:
            found_nadooit_api_key = NadooitApiKey.objects.get(api_key=hashed_api_key, is_active = True)
           
            if found_nadooit_api_key.user.user_code == request.data.get('NADOOIT__USER_CODE'):
                return Response({"error": "Your User code is not valid"}, status=400)
            
            if found_nadooit_api_key.user.user_code != request.data.get('NADOOIT__USER_CODE') and not found_nadooit_api_key.user.is_active:
                return Response({"error": "Your User is not active"}, status=400)
            else:
                try:
                    obj = User.objects.get(user_code=request.data.get('NADOOIT__USER_CODE_TO_CHECK'))
                    
                    if obj.is_active:
                        return Response({"success": "User to check is active"}, status=200)
                    else:
                        return Response({"success": "User to check is not active"}, status=400)
                    
                except User.DoesNotExist:
                    return Response({"error": "User does not exist"}, status=400)	
                 
        except NadooitApiKey.DoesNotExist:	    
            return Response({"error": "Invalid API Key"}, status=401)
    except:
        return Response({"error": "Invalid request"}, status=400)


