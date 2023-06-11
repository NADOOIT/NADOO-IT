from django.urls import path
from bot_management.views import *
from plattforms.telegram.views import telegram_webhook


app_name = "bot_management"

urlpatterns = [
    # telegram
    path(
        "telegram/webhook/<str:secret_url>", telegram_webhook, name="telegram-webhook"
    ),
    # whatsapp
    # ebay
]
