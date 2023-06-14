from bot_management.plattforms.telegram.utils import register_bot_route
from django.views.decorators.csrf import csrf_exempt
from bot_management.plattforms.telegram.api import send_message
import re
from django.http import HttpResponse, JsonResponse


@register_bot_route("24a8ff21-ab91-4f53-b0c9-3a9b4fcb7b6a")
@csrf_exempt
def handle_message(request, *args, token=None, **kwargs):
    # check if message is a command
    text = request.data["message"]["text"]

    if text.startswith("/"):
        # check if command is known
        send_message(
            chat_id=request.data["message"]["chat"]["id"],
            text="Your command is my plessure",
            token=token,
        )
    # check if the message contains a sequence of words
    # check if the text contains "Who are you?"
    elif re.search(r"Who are you\?", text):
        send_message(
            chat_id=request.data["message"]["chat"]["id"],
            text="I AM KING!",
            token=token,
        )
    return HttpResponse("OK")
