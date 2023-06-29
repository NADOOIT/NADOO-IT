from bot_management.core.wisper import transcribe_audio_file
from bot_management.models import (
    User,
    Chat,
    Voice,
    VoiceFile,
    Message,
    BotPlatform,
    PhotoMessage,
    TelegramPhoto,
)
from functools import wraps
from django.db.models import ObjectDoesNotExist
from django.http import HttpResponse
from datetime import datetime
import time
import os
from typing import Dict, Optional, Union
from typing import Any, Optional
from datetime import datetime
from bot_management.models import BotPlatform, Message


bot_routes_telegram = {}


def register_bot_route(secret_url):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            token = BotPlatform.objects.get(secret_url=secret_url).access_token
            kwargs["token"] = token
            return view_func(request, *args, **kwargs)

        bot_routes_telegram[secret_url] = _wrapped_view
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
            # Handle photo field
            if field == "photo":
                # First, get or create the PhotoMessage object
                photo_message, created = PhotoMessage.objects.get_or_create(
                    message=message,
                    # Also set the caption if it exists
                    defaults={"caption": kwargs.get("caption", None)},
                )

                # For each photo in the value list
                for photo_dict in value:
                    # Try to get the existing TelegramPhoto object
                    telegram_photo, created = TelegramPhoto.objects.get_or_create(
                        photo_message=photo_message,
                        file_id=photo_dict.get("file_id"),
                        file_unique_id=photo_dict.get("file_unique_id"),
                        file_size=photo_dict.get("file_size"),
                        width=photo_dict.get("width"),
                        height=photo_dict.get("height"),
                    )
                    if not created:
                        # If the TelegramPhoto already exists, update its fields
                        telegram_photo.file_id = photo_dict.get("file_id")
                        telegram_photo.file_unique_id = photo_dict.get("file_unique_id")
                        telegram_photo.file_size = photo_dict.get("file_size")
                        telegram_photo.width = photo_dict.get("width")
                        telegram_photo.height = photo_dict.get("height")
                        telegram_photo.save()

            # Skip caption field for message attribute check
            elif field != "caption":
                # Check if the values are different
                if getattr(message, field) != value:
                    setattr(message, field, value)
                    changed = True

        if changed:
            message.save()

    except Message.DoesNotExist:
        # The message does not exist, create it
        if "photo" in kwargs:
            # If the message has a photo remove it from the kwargs. Photo is handeled after the message is created.
            photo = kwargs.pop("photo")
        else:
            photo = None
            
        if "caption" in kwargs:
            caption = kwargs.pop("caption")	
        else:	
            caption = None	

        message = Message.objects.create(
            update_id=update_id,  # This will be None if update_id was not provided
            message_id=message_id,
            date=date,
            bot_platform=bot_platform,
            **kwargs,
        )

        if photo is not None:
            # Create a PhotoMessage object
            photo_message = PhotoMessage.objects.create(
                message=message, caption=caption
            )

            # Create TelegramPhoto objects for each photo in the photo list
            for photo_dict in photo:
                TelegramPhoto.objects.create(
                    photo_message=photo_message,
                    file_id=photo_dict.get("file_id"),
                    file_unique_id=photo_dict.get("file_unique_id"),
                    file_size=photo_dict.get("file_size"),
                    width=photo_dict.get("width"),
                    height=photo_dict.get("height"),
                )

    return message


def get_message_for_request(request, *args, token=None, **kwargs):
    from bot_management.plattforms.telegram.api import get_file
    from bot_management.plattforms.telegram.api import get_file_info

    data = request.data

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

        # check if group or private chat
        # Group example 'chat': {'id': -909636733, 'title': 'WebChat1', 'type': 'group', 'all_members_are_administrators': True}
        if chat_data["type"] == "group":
            chat, _ = Chat.objects.get_or_create(
                id=chat_data["id"],
                defaults={
                    "title": chat_data["title"],
                    "type": chat_data["type"],
                    "all_members_are_administrators": chat_data[
                        "all_members_are_administrators"
                    ],
                },
            )
        else:
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

        text = None

        # check if there is text in the message
        if "text" in message_data:
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
