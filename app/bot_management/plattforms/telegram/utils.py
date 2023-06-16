from bot_management.plattforms.telegram.api import get_file
from bot_management.plattforms.telegram.api import get_file_info
from bot_management.core.wisper import transcribe_audio_file
from bot_management.models import User, Chat, Voice, VoiceFile, Message
from bot_management.models import BotPlatform
from functools import wraps

bot_routes = {}


def register_bot_route(secret_url):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            token = BotPlatform.objects.get(secret_url=secret_url).access_token
            kwargs["token"] = token
            return view_func(request, *args, **kwargs)

        bot_routes[secret_url] = _wrapped_view
        return _wrapped_view

    return decorator


from django.db.models import ObjectDoesNotExist
from django.http import HttpResponse
from datetime import datetime
import time
import os


def get_message_for_request(request, *args, token=None, **kwargs):
    data = request.data

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

        if "voice" in message_data:
            voice_info = message_data["voice"]

            # Create the voice instance
            voice, _ = Voice.objects.get_or_create(
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
                from django.core.files.base import ContentFile

                voice_file = ContentFile(voice_file_content, name="voice_file.oga")

                # Create the VoiceFile instance
                new_VoiceFile = VoiceFile.objects.create(
                    voice=voice,
                    file=voice_file,
                )

                while not os.path.exists(new_VoiceFile.file.path):
                    time.sleep(1)

                text = transcribe_audio_file(new_VoiceFile.file)

        additional_info = message_data.get("entities")

        # Now, all operations that might fail have succeeded. It's safe to create the message
        message, _ = Message.objects.get_or_create(
            update_id=data.get("update_id"),
            message_id=message_data["message_id"],
            from_user=user,
            chat=chat,
            date=date,
            text=text,
            voice=voice,
            bot_platform=bot_platform,
            customer=customer,
            additional_info=additional_info,
        )
        return message

    else:
        # Respond with an error or handle as needed
        return HttpResponse("Invalid data. No 'message' found.", status=400)
