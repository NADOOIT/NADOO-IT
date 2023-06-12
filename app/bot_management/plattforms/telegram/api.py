import requests
from typing import Optional, Dict, Any
from requests.models import Response

from dataclasses import dataclass
from typing import Optional, List


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
    return WebhookInfo(**webhook_info_data)


from typing import Optional, List


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
