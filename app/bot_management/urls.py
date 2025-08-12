from django.urls import path
from django.conf import settings
from bot_management.plattforms.telegram.views import telegram_webhook


app_name = "bot_management"

urlpatterns = [
    # telegram
    path(
        "telegram/webhook/<str:bot_register_id>",
        telegram_webhook,
        name="telegram-webhook",
    ),
    # whatsapp
    # ebay
]

# Register WhatsApp webhook route only if explicitly enabled.
if getattr(settings, "WHATSAPP_ENABLED", False):
    from bot_management.plattforms.whatsapp.views import whatsapp_webhook

    urlpatterns += [
        path(
            "whatsapp/webhook/<str:bot_register_id>",
            whatsapp_webhook,
            name="whatsapp-webhook",
        )
    ]
