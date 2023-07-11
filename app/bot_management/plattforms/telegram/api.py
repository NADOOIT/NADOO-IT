from datetime import datetime
from django.http import HttpResponse
import re
import requests
from typing import Optional, Dict, Any
from requests.models import Response

from dataclasses import dataclass
from typing import Dict, Optional, Union, List
from bot_management.models import *

from bot_management.models import *
from bot_management.plattforms.telegram.utils import (
    get_bot_platform_by_token,
    get_or_create_user_from_data,
    get_or_create_and_update_message,
)


@dataclass
class WebhookInfo:
    url: str
    has_custom_certificate: bool
    pending_update_count: int
    ip_address: Optional[str]
    last_error_date: Optional[int]
    last_error_message: Optional[str]
    last_synchronization_error_date: Optional[int]
    max_connections: Optional[int]
    allowed_updates: Optional[List[str]]


def get_webhook_info(bot_token: str) -> Optional[WebhookInfo]:
    """Gets the current webhook info.

    Args:
        bot_token (str): The token of the bot on the Telegram platform.

    Returns:
        WebhookInfo: The current webhook information if successful. Returns None otherwise.
    """
    get_webhook_info_url = f"https://api.telegram.org/bot{bot_token}/getWebhookInfo"

    try:
        response: Response = requests.get(get_webhook_info_url)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Failed to get webhook info: {e}")
        return None

    webhook_info_result = response.json()
    if not webhook_info_result.get("ok"):
        print(
            "Failed to get webhook info:",
            webhook_info_result.get("description", "Unknown error"),
        )
        return None

    webhook_info_data = webhook_info_result.get("result")

    # provide default values for fields that might be missing
    webhook_info_data.setdefault("ip_address", None)
    webhook_info_data.setdefault("last_error_date", None)
    webhook_info_data.setdefault("last_error_message", None)
    webhook_info_data.setdefault("last_synchronization_error_date", None)
    webhook_info_data.setdefault("max_connections", None)
    webhook_info_data.setdefault("allowed_updates", None)

    return WebhookInfo(**webhook_info_data)


def set_webhook(
    bot_token: str,
    webhook_url: str,
    certificate: Optional[str] = None,
    ip_address: Optional[str] = None,
    max_connections: Optional[int] = None,
    allowed_updates: Optional[List[str]] = None,
    drop_pending_updates: Optional[bool] = None,
    secret_token: Optional[str] = None,
) -> bool:
    """Sets the webhook for the bot.

    Args:
        bot_token (str): The token of the bot on the Telegram platform.
        webhook_url (str): The URL of the webhook endpoint.
        certificate (str, optional): Public key certificate.
        ip_address (str, optional): Fixed IP address for sending webhook requests.
        max_connections (int, optional): Maximum allowed number of simultaneous HTTPS connections.
        allowed_updates (List[str], optional): List of the update types the bot should receive.
        drop_pending_updates (bool, optional): If True, drop all pending updates.
        secret_token (str, optional): Secret token to be sent in a header in every webhook request.

    Returns:
        bool: True if the webhook was set up successfully, False otherwise.
    """
    set_webhook_url = f"https://api.telegram.org/bot{bot_token}/setWebhook"
    payload = {
        "url": webhook_url,
        "certificate": certificate,
        "ip_address": ip_address,
        "max_connections": max_connections,
        "allowed_updates": allowed_updates,
        "drop_pending_updates": drop_pending_updates,
        "secret_token": secret_token,
    }
    payload = {k: v for k, v in payload.items() if v is not None}

    try:
        response: Response = requests.post(set_webhook_url, json=payload)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Failed to set up webhook: {e}")
        return False

    set_webhook_result = response.json()
    if not set_webhook_result.get("ok"):
        print(
            "Failed to set up webhook:",
            set_webhook_result.get("description", "Unknown error"),
        )
        return False

    return True


def send_message(
    token: str,
    chat_id: int,
    text: str,
    message_thread_id: Optional[int] = None,
    parse_mode: Optional[str] = None,
    entities: Optional[str] = None,
    disable_web_page_preview: Optional[bool] = None,
    disable_notification: Optional[bool] = None,
    protect_content: Optional[bool] = None,
    reply_to_message_id: Optional[int] = None,
    allow_sending_without_reply: Optional[bool] = None,
    reply_markup: Optional[str] = None,
) -> Union[HttpResponse, TelegramMessage]:
    base_url = f"https://api.telegram.org/bot{token}/sendMessage"

    # Construct the message payload
    payload = {
        "chat_id": chat_id,
        "text": text,
        "message_thread_id": message_thread_id,
        "parse_mode": parse_mode,
        "entities": entities,
        "disable_web_page_preview": disable_web_page_preview,
        "disable_notification": disable_notification,
        "protect_content": protect_content,
        "reply_to_message_id": reply_to_message_id,
        "allow_sending_without_reply": allow_sending_without_reply,
        "reply_markup": reply_markup,
    }

    # Remove None values from the payload
    payload = {k: v for k, v in payload.items() if v is not None}

    # Send the request
    response = requests.post(base_url, json=payload)

    print(response.json())

    # Handle the response
    if response.status_code == 200:
        response_json = response.json()
        message_data = response_json["result"]

        bot_platform = get_bot_platform_by_token(token)

        if bot_platform is None:
            return HttpResponse("Invalid token.", status=400)

        if bot_platform.bot is None:
            return HttpResponse(
                "Bot associated with the platform does not exist.", status=400
            )

        if bot_platform.bot.customer is None:
            return HttpResponse(
                "Customer associated with the bot does not exist.", status=400
            )

        user_data = message_data["from"]
        user = get_or_create_user_from_data(user_data)

        chat_data = message_data["chat"]
        chat, _ = TelegramChat.objects.get_or_create(
            id=chat_data["id"],
            defaults={
                "first_name": chat_data["first_name"],
                "last_name": chat_data.get("last_name"),
                "type": chat_data["type"],
            },
        )

        # use an f sting to print response_json
        print(f"response_json: {response_json}")

        # Get, create or update the Message instance
        message = get_or_create_and_update_message(
            message_id=message_data["message_id"],
            date=datetime.fromtimestamp(message_data["date"]),
            from_user=user,
            chat=chat,
            text=message_data.get("text", ""),
        )

        return message

    else:
        return HttpResponse(response.text, status=400)


def get_file_info(token, file_id):
    base_url = f"https://api.telegram.org/bot{token}/getFile"

    # Construct the message payload
    payload = {
        "file_id": file_id,
    }

    # Remove None values from the payload
    payload = {k: v for k, v in payload.items() if v is not None}

    # Send the request
    response = requests.post(base_url, json=payload)

    # Handle the response
    if response.status_code == 200:
        return response.json()

    else:
        return response.text


def get_file(token, file_path):
    file_url = f"https://api.telegram.org/file/bot{token}/{file_path}"

    response = requests.get(file_url)

    # Ensure the request was successful
    response.raise_for_status()

    return response.content


""" 
editMessageCaption
Use this method to edit captions of messages. On success, if the edited message is not an inline message, the edited Message is returned, otherwise True is returned.

Parameter	Type	Required	Description
chat_id	Integer or String	Optional	Required if inline_message_id is not specified. Unique identifier for the target chat or username of the target channel (in the format @channelusername)
message_id	Integer	Optional	Required if inline_message_id is not specified. Identifier of the message to edit
inline_message_id	String	Optional	Required if chat_id and message_id are not specified. Identifier of the inline message
caption	String	Optional	New caption of the message, 0-1024 characters after entities parsing
parse_mode	String	Optional	Mode for parsing entities in the message caption. See formatting options for more details.
caption_entities	Array of MessageEntity	Optional	A JSON-serialized list of special entities that appear in the caption, which can be specified instead of parse_mode
reply_markup	InlineKeyboardMarkup	Optional	A JSON-serialized object for an inline keyboard.
"""


def edit_message_caption(
    token: str,
    message: TelegramMessage,
    caption: Optional[str] = None,
    parse_mode: Optional[str] = None,
    caption_entities: Optional[str] = None,
    reply_markup: Optional[str] = None,
) -> Union[HttpResponse, TelegramMessage]:
    base_url = f"https://api.telegram.org/bot{token}/editMessageCaption"

    chat_id = message.chat.id
    message_id = message.message_id

    print(f"chat_id: {chat_id}")
    print(f"message_id: {message_id}")

    payload = {
        "chat_id": chat_id,
        "message_id": message_id,
        "caption": caption,
        "parse_mode": parse_mode,
        "caption_entities": caption_entities,
        "reply_markup": reply_markup,
    }

    # Remove None values from the payload
    payload = {k: v for k, v in payload.items() if v is not None}

    # Send the request
    response = requests.post(base_url, json=payload)

    # Handle the response
    if response.status_code == 200:
        response_json = response.json()
        message_data = response_json["result"]

        bot_platform = get_bot_platform_by_token(token)

        if bot_platform is None:
            return HttpResponse("Invalid token.", status=400)

        if bot_platform.bot is None:
            return HttpResponse(
                "Bot associated with the platform does not exist.", status=400
            )

        if bot_platform.bot.customer is None:
            return HttpResponse(
                "Customer associated with the bot does not exist.", status=400
            )

        user_data = message_data["from"]
        user = get_or_create_user_from_data(user_data)

        chat_data = message_data["chat"]
        chat, _ = TelegramChat.objects.get_or_create(
            id=chat_data["id"],
            defaults={
                "first_name": chat_data["first_name"],
                "last_name": chat_data.get("last_name"),
                "type": chat_data["type"],
            },
        )

        print(f"response_json: {response_json}")

        message = get_or_create_and_update_message(
            message_id=message_data["message_id"],
            date=datetime.fromtimestamp(message_data["edit_date"]),
            from_user=user,
            chat=chat,
            caption=message_data.get("caption"),
        )

        return message

    else:
        return HttpResponse(response.text, status=400)


def edit_message_text(
    token: str,
    message: TelegramMessage,
    text: str,
    parse_mode: Optional[str] = None,
    entities: Optional[str] = None,
    disable_web_page_preview: Optional[bool] = None,
    reply_markup: Optional[str] = None,
) -> Union[HttpResponse, TelegramMessage]:
    base_url = f"https://api.telegram.org/bot{token}/editMessageText"

    chat_id = message.chat.id
    message_id = message.message_id

    print(f"chat_id: {chat_id}")
    print(f"message_id: {message_id}")

    payload = {
        "chat_id": chat_id,
        "message_id": message_id,
        "text": text,
        "parse_mode": parse_mode,
        "entities": entities,
        "disable_web_page_preview": disable_web_page_preview,
        "reply_markup": reply_markup,
    }

    # Remove None values from the payload
    payload = {k: v for k, v in payload.items() if v is not None}

    # Send the request
    response = requests.post(base_url, json=payload)

    # Handle the response
    if response.status_code == 200:
        response_json = response.json()
        message_data = response_json["result"]

        bot_platform = get_bot_platform_by_token(token)

        if bot_platform is None:
            return HttpResponse("Invalid token.", status=400)

        if bot_platform.bot is None:
            return HttpResponse(
                "Bot associated with the platform does not exist.", status=400
            )

        if bot_platform.bot.customer is None:
            return HttpResponse(
                "Customer associated with the bot does not exist.", status=400
            )

        user_data = message_data["from"]
        user = get_or_create_user_from_data(user_data)

        chat_data = message_data["chat"]
        chat, _ = TelegramChat.objects.get_or_create(
            id=chat_data["id"],
            defaults={
                "first_name": chat_data["first_name"],
                "last_name": chat_data.get("last_name"),
                "type": chat_data["type"],
            },
        )

        print(f"response_json: {response_json}")

        message = get_or_create_and_update_message(
            message_id=message_data["message_id"],
            date=datetime.fromtimestamp(message_data["edit_date"]),
            from_user=user,
            chat=chat,
            text=message_data.get("text", ""),
        )

        return message

    else:
        return HttpResponse(response.text, status=400)


def edit_message_reply_markup(
    token: str,
    chat_id: Optional[Union[int, str]] = None,
    message_id: Optional[int] = None,
    inline_message_id: Optional[str] = None,
    reply_markup: Optional[str] = None,
    parse_mode: Optional[str] = None,
) -> Union[TelegramMessage, bool]:
    base_url = f"https://api.telegram.org/bot{token}/editMessageReplyMarkup"

    # Construct the message payload
    payload = {
        "chat_id": chat_id,
        "message_id": message_id,
        "inline_message_id": inline_message_id,
        "reply_markup": reply_markup,
    }

    # Remove None values from the payload
    payload = {k: v for k, v in payload.items() if v is not None}

    # Send the request
    response = requests.post(base_url, json=payload)

    # Handle the response
    if response.status_code == 200:
        response_json = response.json()
        result = response_json["result"]

        # Update the message in the database if the result is a Message object
        if isinstance(result, dict):
            # Assumes that the message_id in the response is the same as in the database
            # You need to get the bot_platform object for the function get_or_create_and_update_message
            # bot_platform = BotPlatform.objects.get(token=token)

            # call get_or_create_and_update_message function to update message object
            message = get_or_create_and_update_message(
                message_id=result["message_id"],
                date=datetime.fromtimestamp(result["date"]),
                parse_mode=parse_mode,
                reply_markup=reply_markup,
                text=result.get("text", ""),
            )
            return message
        else:
            return result
    else:
        raise Exception(
            f"Request failed with status code {response.status_code}. Response: {response.text}"
        )


""" sendPhoto
Use this method to send photos. On success, the sent Message is returned.

Parameter	Type	Required	Description
chat_id	Integer or String	Yes	Unique identifier for the target chat or username of the target channel (in the format @channelusername)
message_thread_id	Integer	Optional	Unique identifier for the target message thread (topic) of the forum; for forum supergroups only
photo	InputFile or String	Yes	Photo to send. Pass a file_id as String to send a photo that exists on the Telegram servers (recommended), pass an HTTP URL as a String for Telegram to get a photo from the Internet, or upload a new photo using multipart/form-data. The photo must be at most 10 MB in size. The photo's width and height must not exceed 10000 in total. Width and height ratio must be at most 20. More information on Sending Files »
caption	String	Optional	Photo caption (may also be used when resending photos by file_id), 0-1024 characters after entities parsing
parse_mode	String	Optional	Mode for parsing entities in the photo caption. See formatting options for more details.
caption_entities	Array of MessageEntity	Optional	A JSON-serialized list of special entities that appear in the caption, which can be specified instead of parse_mode
has_spoiler	Boolean	Optional	Pass True if the photo needs to be covered with a spoiler animation
disable_notification	Boolean	Optional	Sends the message silently. Users will receive a notification with no sound.
protect_content	Boolean	Optional	Protects the contents of the sent message from forwarding and saving
reply_to_message_id	Integer	Optional	If the message is a reply, ID of the original message
allow_sending_without_reply	Boolean	Optional	Pass True if the message should be sent even if the specified replied-to message is not found
reply_markup	InlineKeyboardMarkup or ReplyKeyboardMarkup or ReplyKeyboardRemove or ForceReply	Optional	Additional interface options. A JSON-serialized object for an inline keyboard, custom reply keyboard, instructions to remove reply keyboard or to force a reply from the user.
"""


def send_photo(
    token: str,
    chat_id: Union[int, str],
    photo: Union[str, bytes],
    caption: Optional[str] = None,
    parse_mode: Optional[str] = None,
    caption_entities: Optional[List[Dict[str, Union[str, int, bool]]]] = None,
    has_spoiler: Optional[bool] = None,
    disable_notification: Optional[bool] = None,
    protect_content: Optional[bool] = None,
    reply_to_message_id: Optional[int] = None,
    allow_sending_without_reply: Optional[bool] = None,
    reply_markup: Optional[Union[str, Dict[str, Any]]] = None,
) -> Union[HttpResponse, TelegramMessage]:
    base_url = f"https://api.telegram.org/bot{token}/sendPhoto"

    # Construct the message payload
    payload = {
        "chat_id": chat_id,
        "photo": photo,
        "caption": caption,
        "parse_mode": parse_mode,
        "caption_entities": caption_entities,
        "has_spoiler": has_spoiler,
        "disable_notification": disable_notification,
        "protect_content": protect_content,
        "reply_to_message_id": reply_to_message_id,
        "allow_sending_without_reply": allow_sending_without_reply,
        "reply_markup": reply_markup,
    }

    # Remove None values from the payload
    payload = {k: v for k, v in payload.items() if v is not None}

    # Send the request
    response = requests.post(base_url, json=payload)
    print("Response from telegram: ")
    print(response)
    print(response.json())
    print("")
    print("")
    print("")
    # Handle the response
    if response.status_code == 200:
        response_json = response.json()
        message_data = response_json["result"]

        bot_platform = get_bot_platform_by_token(token)

        if bot_platform is None:
            return HttpResponse("Invalid token.", status=400)

        if bot_platform.bot is None:
            return HttpResponse(
                "Bot associated with the platform does not exist.", status=400
            )

        if bot_platform.bot.customer is None:
            return HttpResponse(
                "Customer associated with the bot does not exist.", status=400
            )

        user_data = message_data["from"]
        user = get_or_create_user_from_data(user_data)

        chat_data = message_data["chat"]
        chat, _ = TelegramChat.objects.get_or_create(
            id=chat_data["id"],
            defaults={
                "first_name": chat_data["first_name"],
                "last_name": chat_data.get("last_name"),
                "type": chat_data["type"],
            },
        )

        # if message contains photo
        if message_data.get("photo"):
            caption = message_data.get("caption")
            message = get_or_create_and_update_message(
                message_id=message_data["message_id"],
                date=datetime.fromtimestamp(message_data["date"]),
                from_user=user,
                chat=chat,
                photo=message_data["photo"],
                caption=caption,
            )

        return message

    else:
        return HttpResponse(response.text, status=400)
