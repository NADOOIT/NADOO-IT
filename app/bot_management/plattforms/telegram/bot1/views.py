from datetime import datetime
from bot_management.plattforms.telegram.utils import get_message_for_request
from bot_management.core.wisper import transcribe_audio_file
from bot_management.plattforms.telegram.api import get_file
from bot_management.models import BotPlatform, Message, Voice, VoiceFile, User, Chat
from bot_management.plattforms.telegram.api import get_file_info
from bot_management.plattforms.telegram.utils import register_bot_route
from django.views.decorators.csrf import csrf_exempt
from bot_management.plattforms.telegram.api import send_message, edit_message
import re
from django.http import HttpResponse, JsonResponse
from django.db import transaction
from django.core.files.base import ContentFile


import time
import os


@register_bot_route("24a8ff21-ab91-4f53-b0c9-3a9b4fcb7b6a")
@csrf_exempt
def handle_message(request, *args, token=None, **kwargs):
    print(request.data)

    message = get_message_for_request(request, *args, token=token, **kwargs)

    if message is not None:
        if message.text.startswith("/update"):
            send_message(
                chat_id=message.chat.id,
                text="Neuen Artikel anlegen. Antworten Sie bitte jeweils auf die folgenden Fragen. Nutzen Sie hierzu Text oder Sprachnachrichten.",
                token=token,
            )

            send_message(
                chat_id=message.chat.id,
                text="Wie lautet der Titel?",
                token=token,
            )

            last_message = send_message(
                chat_id=message.chat.id,
                text="Wie lautet die Beschreibung?",
                token=token,
            )

            edit_message(
                chat_id=last_message.chat.id,
                message_id=last_message.message_id,
                text="Hab die nachricht geändert",
                token=token,
            )

        else:
            send_message(
                chat_id=message.chat.id,
                text=message.text,
                token=token,
            )
