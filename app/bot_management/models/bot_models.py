from typing import Type
from django.db import models
from django.db.models.options import Options
from nadoo_erp.models import Item
from nadooit_crm.models import Customer
from uuid import uuid4
from django.dispatch import receiver
from django.db.models.signals import pre_delete

# Options
PLATFORM_CHOICES = [
    ("telegram", "Telegram"),
    ("facebook", "Facebook Messenger"),
    ("whatsapp", "WhatsApp"),
    # add more platforms as needed
]


class Bot(models.Model):
    name = models.CharField(max_length=100, unique=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)


class BotPlatform(models.Model):
    bot = models.ForeignKey(Bot, on_delete=models.CASCADE)
    platform = models.CharField(max_length=50, choices=PLATFORM_CHOICES)
    bot_register_id = models.UUIDField(default=uuid4, unique=True, editable=False)
    access_token = models.CharField(max_length=100)
    secret_token = models.UUIDField(default=uuid4, unique=True, editable=False)
    phone_number = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.bot.name + " - " + self.platform


class APIKey(models.Model):
    bot_platform = models.ForeignKey(BotPlatform, on_delete=models.CASCADE)
    api_key = models.UUIDField(default=uuid4, unique=True, editable=False)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name + " - " + str(self.api_key)
