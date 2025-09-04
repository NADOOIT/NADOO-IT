from django.urls import path
from bot_management.plattforms.telegram.views import telegram_webhook
from bot_management.plattforms.whatsapp.views import whatsapp_webhook


app_name = "bot_management"

urlpatterns = [
    # telegram
    path(
        "telegram/webhook/<str:bot_register_id>",
        telegram_webhook,
        name="telegram-webhook",
    ),
    path(
        "whatsapp/webhook/<str:bot_register_id>",
        whatsapp_webhook,
        name="whatsapp-webhook",
    ),
    # whatsapp
    # ebay
]
