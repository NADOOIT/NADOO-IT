from django.http import HttpResponse


import re
from rest_framework.decorators import api_view
from rest_framework.response import Response

# list of all whatsapp bots
from bot_management.plattforms.whatsapp.utils import whatsapp_bots

# register bot views by importing them
from bot_management.plattforms.whatsapp.bot1.bot import bot
from django.views.decorators.csrf import csrf_exempt


from django.http import JsonResponse


@csrf_exempt
def whatsapp_webhook(request, bot_register_id):
    print("whatsapp_webhook")

    # bot/whatsapp/webhook/3cfa80bb-f3c1-49ff-bf1d-2f51f5f22138?hub.mode=subscribe&hub.challenge=1382766763&hub.verify_token=e1f234bd-dd69-4938-ae16-f9b27807e819

    print(request)
    print(bot_register_id)
    print(whatsapp_bots)

    if bot_register_id not in whatsapp_bots:
        return JsonResponse({"error": "Unknown bot"}, status=404)

    print("bot_routes_whatsapp[bot_register_id](request)")

    view_func = whatsapp_bots[bot_register_id]

    print(view_func)
    print("GOT HERE")
    return view_func(request)
