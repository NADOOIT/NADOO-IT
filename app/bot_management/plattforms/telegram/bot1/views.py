from datetime import datetime
from bot_management.plattforms.telegram.utils import get_message_for_request
from bot_management.core.wisper import transcribe_audio_file
from bot_management.plattforms.telegram.api import get_file
from bot_management.models import BotPlatform, Message, Voice, VoiceFile, User, Chat
from bot_management.plattforms.telegram.api import get_file_info
from bot_management.plattforms.telegram.utils import register_bot_route
from django.views.decorators.csrf import csrf_exempt
from bot_management.plattforms.telegram.api import send_message
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

            send_message(
                chat_id=message.chat.id,
                text="Wie lautet die Beschreibung?",
                token=token,
            )

        send_message(
            chat_id=message.chat.id,
            text=message.text,
            token=token,
        )

    return HttpResponse("OK")

    data = request.data

    print(data)

    if "message" in data:
        message_data = data["message"]

        # Get or create user from message
        user_data = message_data["from"]
        user, _ = User.objects.get_or_create(
            id=user_data["id"],
            defaults={
                "is_bot": user_data["is_bot"],
                "first_name": user_data["first_name"],
                "last_name": user_data.get("last_name"),
                "language_code": user_data.get("language_code"),
            },
        )

        # Get or create chat from message
        chat_data = message_data["chat"]
        chat, _ = Chat.objects.get_or_create(
            id=chat_data["id"],
            defaults={
                "first_name": chat_data["first_name"],
                "last_name": chat_data.get("last_name"),
                "type": chat_data["type"],
            },
        )

        # If 'date' is a timestamp (seconds since epoch), convert to datetime
        if isinstance(message_data["date"], (int, float)):
            date = datetime.fromtimestamp(message_data["date"])
        else:
            print(f"Unexpected date format: {message_data['date']}")
            date = None  # or set to some default value

        # Identify the BotPlatform by token (secret_url)
        try:
            bot_platform = BotPlatform.objects.get(access_token=token)
        except BotPlatform.DoesNotExist:
            # Respond with an error or handle as needed
            return HttpResponse("Invalid token.", status=400)

        customer = bot_platform.bot.customer
        text = message_data.get("text", "")
        voice = None

        if text.startswith("/"):
            send_message(
                chat_id=chat.id,
                text="Your command is my pleasure",
                token=token,
            )
        elif re.search(r"Who are you\?", text):
            send_message(
                chat_id=chat.id,
                text="I AM KING!",
                token=token,
            )

        if "voice" in message_data:
            voice_info = message_data["voice"]

            # Create the voice instance
            voice = Voice.objects.create(
                duration=voice_info["duration"],
                mime_type=voice_info["mime_type"],
                file_id=voice_info["file_id"],
                file_unique_id=voice_info["file_unique_id"],
                file_size=voice_info["file_size"],
            )

            voice_file_info = get_file_info(token, voice_info["file_id"])

            if "file_path" in voice_file_info["result"]:
                voice_file_content = get_file(
                    token, voice_file_info["result"]["file_path"]
                )

                # Save binary content to a Django ContentFile with a specified name
                voice_file = ContentFile(voice_file_content, name="voice_file.oga")

                # Create the VoiceFile instance
                new_VoiceFile = VoiceFile.objects.create(
                    voice=voice,
                    file=voice_file,
                )

                while not os.path.exists(new_VoiceFile.file.path):
                    time.sleep(1)

                text = transcribe_audio_file(new_VoiceFile.file)

                send_message(
                    chat_id=chat.id,
                    text=text,
                    token=token,
                )

            else:
                send_message(
                    chat_id=chat.id,
                    text="What did you say? >.<*",
                    token=token,
                )

        # Now, all operations that might fail have succeeded. It's safe to create the message instance.
        with transaction.atomic():
            message, created = Message.objects.get_or_create(
                update_id=data["update_id"],
                message_id=message_data["message_id"],
                date=date,
                from_user=user,
                chat=chat,
                customer=customer,
                bot_platform=bot_platform,
                defaults={
                    "text": text,
                    "voice": voice,
                    "additional_info": message_data.get("entities"),
                },
            )

    return HttpResponse("OK")
