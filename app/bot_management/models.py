from django.db import models

from nadooit_crm.models import Customer

# Options
PLATFORM_CHOICES = [
    ("telegram", "Telegram"),
    ("facebook", "Facebook Messenger"),
    ("whatsapp", "WhatsApp"),
    # add more platforms as needed
]


# Create your models here.
class Bot(models.Model):
    name = models.CharField(max_length=100, unique=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)


class BotPlatform(models.Model):
    bot = models.ForeignKey(Bot, on_delete=models.CASCADE)
    platform = models.CharField(max_length=50, choices=PLATFORM_CHOICES)
    access_token = models.CharField(max_length=100)
    api_key = models.CharField(max_length=100, unique=True)
    secret_url = models.CharField(max_length=200, unique=True)
