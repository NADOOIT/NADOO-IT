# bot_management/views.py
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from bot_management.models import BotPlatform

# register telegram bots by importing them
from bot_management.plattforms.telegram.bot import bot


@api_view(["POST"])
@csrf_exempt
def telegram_webhook(request, bot_register_id):
    bot_platform = get_object_or_404(BotPlatform, bot_register_id=bot_register_id)
    access_token = bot_platform.access_token
    return bot(request, bot_register_id, token=access_token)
