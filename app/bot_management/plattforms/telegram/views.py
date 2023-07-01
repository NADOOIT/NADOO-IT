from rest_framework.decorators import api_view

# register telegram bots by importing them
from bot_management.plattforms.telegram.bot import bot

from django.http import JsonResponse

from django.views.decorators.csrf import csrf_exempt

# New version
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from bot_management.models import BotPlatform
from bot_management.plattforms.telegram.utils import *


# views.py
@api_view(["POST"])
@csrf_exempt
def telegram_webhook(request, bot_register_id):
    print("telegram_webhook")

    print(f"Bot register id: {bot_register_id}")

    try:
        bot_platform = BotPlatform.objects.get(bot_register_id=bot_register_id)
        access_token = bot_platform.access_token
    except BotPlatform.DoesNotExist:
        return JsonResponse({"error": "Unknown bot"}, status=404)

    return bot(request, bot_register_id, token=access_token)
