from django.http import HttpResponse


import re
from rest_framework.decorators import api_view
from rest_framework.response import Response

# list of all telegram bots
from bot_management.plattforms.telegram.utils import telegram_bots

# register telegram bots by importing them
from bot_management.plattforms.telegram.bot1.bot import bot


from django.http import JsonResponse

from django.views.decorators.csrf import csrf_exempt


@api_view(["POST"])
@csrf_exempt
def telegram_webhook(request, bot_register_id):
    print("telegram_webhook")

    if bot_register_id not in telegram_bots:
        return JsonResponse({"error": "Unknown bot"}, status=404)
    return telegram_bots[bot_register_id](request)
