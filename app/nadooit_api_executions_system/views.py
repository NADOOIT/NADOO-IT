# Author: Christoph Backhaus
# Date: 2022-10-30
# Version: 1.0.0
# Description: This is the views file for the nadooit_api_executions_system. Here you can register views for apis
# Compatibility: Django 4
# License: TBD

from nadooit_hr.models import EmployeeContract
from rest_framework.decorators import api_view
from rest_framework.response import Response
from nadooit_api_executions_system.models import CustomerProgramExecution
from nadooit_api_key.models import NadooitApiKey
from nadooit_auth.models import User
from nadooit_program_ownership_system.models import CustomerProgram
from nadooit_os.services import (
    get__nadooit_api_key__for__hashed_api_key,
    get__hashed_api_key__for__request,
    check__nadooit_api_key__has__is_active,
    get__user_code__for__nadooit_api_key,
    get__new_price_per_second__for__customer_program,
    get__price_for_execution__for__cutomer_program,
)


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
    try:
        # gets the hashed api key from the request
        hashed_api_key = get__hashed_api_key__for__request(request)

        try:
            # checks if the api key is active
            if check__nadooit_api_key__has__is_active(hashed_api_key):

                nadooit_api_key = get__nadooit_api_key__for__hashed_api_key(
                    hashed_api_key
                )

                user_code__for__nadooit_api_key = get__user_code__for__nadooit_api_key(
                    nadooit_api_key
                )
                user_code__for__request = get__user_code__for__request(request)

                # checks if the user code in the request is the same user code that is registered in the api key
                if user_code__for__nadooit_api_key != user_code__for__request:
                    return Response({"error": "User code is not valid"}, status=400)

                # checks if the user code is active in the system
                if (
                    user_code__for__nadooit_api_key == user_code__for__request
                    and not nadooit_api_key.user.is_active
                ):
                    return Response({"error": "User is not active"}, status=400)
                else:
                    # check if customer program exists
                    if not CustomerProgram.objects.filter(
                        id=request.data["program_id"]
                    ).exists():
                        return Response({"error": "Program does not exist"}, status=400)

                    nadooit_customer_program = CustomerProgram.objects.get(
                        id=request.data["program_id"]
                    )

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

                    price_for_execution = (
                        get__price_for_execution__for__cutomer_program(
                            nadooit_customer_program
                        )
                    )

                    nadooit_customer_program_execution = CustomerProgramExecution.objects.create(
                        program_time_saved_in_seconds=nadooit_customer_program.program_time_saved_per_execution_in_seconds,
                        customer_program=nadooit_customer_program,
                        price_per_second_at_the_time_of_execution=nadooit_customer_program.price_per_second,
                        price_for_execution=price_for_execution,
                    )

                    nadooit_customer_program.price_per_second = (
                        get__new_price_per_second__for__customer_program(
                            nadooit_customer_program_execution.customer_program
                        )
                    )

                    nadooit_customer_program.save()

                    return Response({"success": "Execution created"}, status=200)

        except NadooitApiKey.DoesNotExist:
            return Response({"error": "Invalid API Key"}, status=401)
    except:
        return Response({"error": "Invalid request"}, status=400)


@api_view(["POST"])
def check_user(request):
    try:
        hashed_api_key = get__hashed_api_key__for__request(request)

        try:
            found_nadooit_api_key = NadooitApiKey.objects.get(
                api_key=hashed_api_key, is_active=True
            )

            if found_nadooit_api_key.user.user_code == request.data.get(
                "NADOOIT__USER_CODE"
            ):
                return Response({"error": "Your User code is not valid"}, status=400)

            if (
                found_nadooit_api_key.user.user_code
                != request.data.get("NADOOIT__USER_CODE")
                and not found_nadooit_api_key.user.is_active
            ):
                return Response({"error": "Your User is not active"}, status=400)
            else:
                try:
                    obj = User.objects.get(
                        user_code=request.data.get("NADOOIT__USER_CODE_TO_CHECK")
                    )

                    if obj.is_active:
                        return Response(
                            {"success": "User to check is active"}, status=200
                        )
                    else:
                        return Response(
                            {"success": "User to check is not active"}, status=400
                        )

                except User.DoesNotExist:
                    return Response({"error": "User does not exist"}, status=400)

        except NadooitApiKey.DoesNotExist:
            return Response({"error": "Invalid API Key"}, status=401)
    except:
        return Response({"error": "Invalid request"}, status=400)
