from datetime import datetime
from django.http import HttpResponse
import requests
from typing import Optional, Dict, Any
from requests.models import Response

from dataclasses import dataclass
from typing import Dict, Optional, Union, List

from bot_management.models import Chat, Message
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
) -> Union[HttpResponse, Message]:
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
        chat, _ = Chat.objects.get_or_create(
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
            bot_platform=bot_platform,
            from_user=user,
            chat=chat,
            text=message_data.get("text", ""),
            customer=bot_platform.bot.customer,
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


def edit_message(
    token: str,
    chat_id: int,
    message_id: int,
    text: str,
    parse_mode: Optional[str] = None,
    entities: Optional[str] = None,
    disable_web_page_preview: Optional[bool] = None,
    reply_markup: Optional[str] = None,
) -> Union[HttpResponse, Message]:
    base_url = f"https://api.telegram.org/bot{token}/editMessageText"

    # Construct the message payload
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
        chat, _ = Chat.objects.get_or_create(
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
            bot_platform=bot_platform,
            from_user=user,
            chat=chat,
            text=message_data.get("text", ""),
            customer=bot_platform.bot.customer,
        )

        return message

    else:
        return HttpResponse(response.text, status=400)
