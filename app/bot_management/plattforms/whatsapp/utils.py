from bot_management.core.wisper import transcribe_audio_file
from bot_management.models import User, Chat, Voice, VoiceFile, Message, BotPlatform
from functools import wraps
from django.http import HttpResponse
from datetime import datetime
import time
import os
from typing import Dict, Optional, Union
from typing import Any, Optional
from datetime import datetime
from bot_management.models import BotPlatform, Message

# TODO: #280 rename to whatsapp_bot_ids
whatsapp_bots = {}


def register_bot(bot_register_id):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # For GET requests (e.g., webhook verification challenges), do not require
            # any database lookups. Simply pass through to the view so it can handle
            # the challenge echo securely without depending on BotPlatform entries.
            if request.method == "GET":
                return view_func(request, *args, **kwargs)

            # For non-GET (e.g., POST message handling), fetch the token. If the
            # BotPlatform is not registered, respond with a 400 to avoid crashing.
            try:
                token = BotPlatform.objects.get(
                    bot_register_id=bot_register_id
                ).access_token
            except BotPlatform.DoesNotExist:
                return HttpResponse("Unknown bot.", status=400)

            kwargs["token"] = token
            return view_func(request, *args, **kwargs)

        whatsapp_bots[bot_register_id] = _wrapped_view
        return _wrapped_view

    return decorator


def get_bot_platform_by_token(token: str) -> Optional[BotPlatform]:
    try:
        bot_platform = BotPlatform.objects.get(access_token=token)
        return bot_platform
    except BotPlatform.DoesNotExist:
        # Respond with an error or handle as needed
        return None


def get_or_create_user_from_data(user_data: Dict) -> User:
    user, _ = User.objects.get_or_create(
        id=user_data["id"],
        defaults={
            "is_bot": user_data["is_bot"],
            "first_name": user_data["first_name"],
            "last_name": user_data.get("last_name"),
            "language_code": user_data.get("language_code"),
        },
    )
    return user


def get_or_create_and_update_message(
    message_id: int,
    date: datetime,
    bot_platform: BotPlatform,
    update_id: Optional[int] = None,  # Make update_id optional
    **kwargs: Any,
) -> Message:
    """
    This function tries to get a message with the provided parameters from the database.
    If the message does not exist, it creates a new one. If the message exists, it compares
    the new parameters with the existing ones, and updates the record if any changes are found.

    :param message_id: The id of the message.
    :param date: The date of the message.
    :param bot_platform: The BotPlatform object of the message.
    :param update_id: The update id of the message. This parameter is now optional.
    :param kwargs: Additional parameters to update in the message.
    :return: The retrieved or updated Message object.
    """
    try:
        print("Trying to get message")
        print(message_id)
        print(date)
        print(bot_platform)

        # Use update_id only if it's not None
        query_params = {
            "message_id": message_id,
            "date": date,
            "bot_platform": bot_platform,
        }
        if update_id is not None:
            query_params["update_id"] = update_id

        message = Message.objects.get(**query_params)

        # The message exists, compare and update if needed
        changed = False
        for field, value in kwargs.items():
            # Check if the values are different
            if getattr(message, field) != value:
                setattr(message, field, value)
                changed = True

        if changed:
            message.save()

    except Message.DoesNotExist:
        # The message does not exist, create it
        message = Message.objects.create(
            update_id=update_id,  # This will be None if update_id was not provided
            message_id=message_id,
            date=date,
            bot_platform=bot_platform,
            **kwargs,
        )

    return message


def get_message_for_request(request, *args, token=None, **kwargs):
    # get all the info that was send in the request
    data = request.POST.dict()

    # check if the data is empty
    if not data:
        # return None if the data is empty
        pass

    return None

    # use an f string to print the data to the console
    print(f"Data in get_message_for_request: {data}")

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

        # Now, all operations that might fail have succeeded. It's safe to create or update the message
        message = get_or_create_and_update_message(
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
