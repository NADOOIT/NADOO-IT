from django.db import models
from nadoo_erp.models import Item

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


class Message(models.Model):
    message_id = models.BigIntegerField()
    text = models.TextField(blank=True, null=True)
    date = models.DateTimeField()
    additional_info = models.JSONField(blank=True, null=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    platform = models.CharField(max_length=255)

    class Meta:
        unique_together = ["message_id", "date", "platform"]

    def __str__(self):
        return f"Message {self.message_id} on {self.platform}"


# These are central models for diffrent kind of messages
class Advertisement(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    messages = models.ManyToManyField("Message")

    def __str__(self):
        return f"Advertisement {self.pk}"
