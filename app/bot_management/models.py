from django.db import models

from nadooit_crm.models import Customer
from uuid import uuid4

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


from uuid import uuid4


class BotPlatform(models.Model):
    bot = models.ForeignKey(Bot, on_delete=models.CASCADE)
    platform = models.CharField(max_length=50, choices=PLATFORM_CHOICES)
    secret_url = models.UUIDField(default=uuid4, unique=True, editable=False)
    access_token = models.CharField(max_length=100)
    secret_token = models.UUIDField(default=uuid4, unique=True, editable=False)


class APIKey(models.Model):
    bot_platform = models.ForeignKey(BotPlatform, on_delete=models.CASCADE)
    api_key = models.UUIDField(default=uuid4, unique=True, editable=False)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name + " - " + str(self.api_key)
