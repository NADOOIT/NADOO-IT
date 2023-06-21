from django.http import HttpResponse


import re
from rest_framework.decorators import api_view
from rest_framework.response import Response


from bot_management.plattforms.telegram.utils import bot_routes_telegram

# register bot views by importing them
from bot_management.plattforms.telegram.bot1.views import handle_message


from django.http import JsonResponse

from django.views.decorators.csrf import csrf_exempt


@api_view(["POST"])
@csrf_exempt
def telegram_webhook(request, secret_url):
    print("telegram_webhook")

    if secret_url not in bot_routes_telegram:
        return JsonResponse({"error": "Unknown bot"}, status=404)
    return bot_routes_telegram[secret_url](request)
