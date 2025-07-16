# Author: Christoph Backhaus
# Date: 2022-10-30
# Version: 1.0.0
# Description: This is the views file for the nadooit_api_executions_system. Here you can register views for apis
# Compatibility: Django 4
# License: TBD

from nadooit_api_executions_system.models import CustomerProgramExecution
from nadooit_api_key.models import NadooitApiKey
from nadooit_auth.models import User
from nadooit_hr.models import EmployeeContract
from nadooit_os.services import (
    check__customer_program__for__customer_program_id__exists,
    check__nadooit_api_key__has__is_active,
    create__customer_program_execution__for__customer_program,
    get__customer_program__for__customer_program_id,
    get__hashed_api_key__for__request,
    get__nadooit_api_key__for__hashed_api_key,
    get__user_code__for__nadooit_api_key)
from nadooit_program_ownership_system.models import CustomerProgram
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


def get__user_code__for__request(request) -> str:

    """

    gets the user code from the request

    Returns:
        _type_: the user code as a string
    """

    return request.data.get("NADOOIT__USER_CODE")


# Create your views here.

# view for creating a new execution
@api_view(["POST"])
def create_execution(request):

    print("create_execution")
    print(request.data)

    try:
        # gets the hashed api key from the request
        hashed_api_key = get__hashed_api_key__for__request(request)
        print("hashed_api_key", hashed_api_key)
        try:
            # checks if the api key is active
            if check__nadooit_api_key__has__is_active(hashed_api_key):
                print("api key is active")

                nadooit_api_key = get__nadooit_api_key__for__hashed_api_key(
                    hashed_api_key
                )

                user_code__for__nadooit_api_key = get__user_code__for__nadooit_api_key(
                    nadooit_api_key
                )
                user_code__for__request = get__user_code__for__request(request)

                # checks if the user code in the request is the same user code that is registered in the api key
                if user_code__for__nadooit_api_key != user_code__for__request:
                    return Response({"error": "User code is not valid"}, status=403)

                print("user code is valid")

                # checks if the user code is active in the system
                if (
                    user_code__for__nadooit_api_key == user_code__for__request
                    and not nadooit_api_key.user.is_active
                ):
                    return Response({"error": "User is not active"}, status=403)
                else:
                    # check if customer program exists
                    if not check__customer_program__for__customer_program_id__exists(
                        request.data["program_id"]
                    ):
                        return Response({"error": "Program does not exist"}, status=400)

                    nadooit_customer_program = (
                        get__customer_program__for__customer_program_id(
                            request.data["program_id"]
                        )
                    )

                    print("customer program exists")

                    # check if the user is an employee of the company that owns the program
                    if not EmployeeContract.objects.filter(
                        employee__user__user_code=user_code__for__request,
                        customer=nadooit_customer_program.customer,
                        is_active=True,
                    ).exists():
                        return Response(
                            {"error": "User is not an employee of the company"},
                            status=400,
                        )

                    print("user is an employee of the company")

                    time_saved_by_this_exection = request.data.get("time_saved", None)


                    if time_saved_by_this_exection:
                        
                        nadooit_customer_program_execution = (
                            create__customer_program_execution__for__customer_program(
                                nadooit_customer_program, int(time_saved_by_this_exection)
                            )
                            
                        )
                    else:
                        nadooit_customer_program_execution = (
                            create__customer_program_execution__for__customer_program(
                                nadooit_customer_program)
                            )
                        
                    return Response({"success": "Execution created"}, status=200)
            else:
                return Response({"error": "Invalid API Key"}, status=403)
        except NadooitApiKey.DoesNotExist:
            return Response({"error": "Invalid API Key"}, status=403)
    except Exception as e:
        print(e)
        return Response({"error": "Invalid request"}, status=400)


@api_view(["POST"])
def check_user(request):
    try:
        hashed_api_key = get__hashed_api_key__for__request(request)

        found_nadooit_api_key = get__nadooit_api_key__for__hashed_api_key(
            hashed_api_key
        )

        if not check__nadooit_api_key__has__is_active(hashed_api_key):
            return Response({"error": "Your API Key is not valid"}, status=403)

        if not found_nadooit_api_key.user.user_code == request.data.get(
            "NADOOIT__USER_CODE"
        ):
            return Response({"error": "Your User code is not valid"}, status=403)

        if (
            found_nadooit_api_key.user.user_code
            != request.data.get("NADOOIT__USER_CODE")
            and not found_nadooit_api_key.user.is_active
        ):
            return Response({"error": "Your User is not active"}, status=403)

        try:
            obj = User.objects.get(
                user_code=request.data.get("NADOOIT__USER_CODE_TO_CHECK")
            )

            if obj.is_active:
                return Response({"success": "User to check is active"}, status=200)
            else:
                return Response({"success": "User to check is not active"}, status=400)
        except User.DoesNotExist:
            return Response({"error": "User does not exist"}, status=400)
    except:
        return Response({"error": "Invalid request"}, status=400)


@api_view(["POST"])
@permission_classes([AllowAny]) # This endpoint is open but validates credentials passed in the body
def validate_user_credentials(request):
    """
    Validates a user's API key and user code.
    This is intended to be called by other internal microservices.
    """
    api_key_header = request.headers.get("NADOOIT-API-KEY")
    user_code = request.data.get("NADOOIT_USER_CODE")

    if not api_key_header or not user_code:
        return Response({"error": "API key and user code are required"}, status=400)

    try:
        # The get__hashed_api_key__for__request function expects the key in a different place,
        # so we perform the hashing and lookup manually here.
        from nadooit_os.services import get__hashed_api_key
        hashed_api_key = get__hashed_api_key(api_key_header)

        nadooit_api_key = get__nadooit_api_key__for__hashed_api_key(hashed_api_key)

        if not nadooit_api_key.is_active:
            return Response({"error": "API key is not active"}, status=403)

        if nadooit_api_key.user.user_code != user_code:
            return Response({"error": "User code does not match API key"}, status=403)

        if not nadooit_api_key.user.is_active:
            return Response({"error": "User is not active"}, status=403)

        # If all checks pass, the credentials are valid
        return Response({"valid": True, "user_code": user_code}, status=200)

    except NadooitApiKey.DoesNotExist:
        return Response({"error": "Invalid API Key"}, status=403)
    except Exception as e:
        # Log the exception for debugging
        print(f"Error during credential validation: {e}")
        return Response({"error": "An internal error occurred"}, status=500)
