from django.urls import path
from bot_management.plattforms.telegram.views import telegram_webhook
from bot_management.plattforms.whatsapp.views import whatsapp_webhook


app_name = "bot_management"

urlpatterns = [
    # telegram
    path(
        "telegram/webhook/<str:secret_url>", telegram_webhook, name="telegram-webhook"
    ),
    path(
        "whatsapp/webhook/<str:secret_url>", whatsapp_webhook, name="whatsapp-webhook"
    ),
    # whatsapp
    # ebay
]
