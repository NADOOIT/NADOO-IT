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


class User(models.Model):
    id = models.BigIntegerField(primary_key=True)
    is_bot = models.BooleanField()
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    language_code = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        if self.last_name:
            return self.first_name + " " + self.last_name
        else:
            return self.first_name

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"


class Chat(models.Model):
    id = models.BigIntegerField(primary_key=True)
    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    type = models.CharField(max_length=255)
    title = models.CharField(max_length=255, blank=True, null=True)
    all_members_are_administrators = models.BooleanField(default=False)


class Bot(models.Model):
    name = models.CharField(max_length=100, unique=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)


class BotPlatform(models.Model):
    bot = models.ForeignKey(Bot, on_delete=models.CASCADE)
    platform = models.CharField(max_length=50, choices=PLATFORM_CHOICES)
    secret_url = models.UUIDField(default=uuid4, unique=True, editable=False)
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


class Voice(models.Model):
    duration = models.IntegerField()
    mime_type = models.CharField(max_length=100)
    file_id = models.CharField(max_length=100)
    file_unique_id = models.CharField(max_length=100)
    file_size = models.IntegerField()

    def __str__(self):
        return f"Voice Message {self.file_id}"


class VoiceFile(models.Model):
    voice = models.OneToOneField(Voice, on_delete=models.CASCADE)
    file = models.FileField(upload_to="voice_files/")

    def __str__(self):
        return f"Voice File {self.voice.file_id}"


# This method will be called before a VoiceFile instance is deleted
@receiver(pre_delete, sender=VoiceFile)
def delete_file_pre_delete(sender, instance, **kwargs):
    instance.file.delete(False)


class Message(models.Model):
    update_id = models.BigIntegerField(unique=True, blank=True, null=True)
    message_id = models.BigIntegerField()
    from_user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="messages", blank=True, null=True
    )
    chat = models.ForeignKey(
        Chat, on_delete=models.CASCADE, related_name="messages", blank=True, null=True
    )
    text = models.TextField(blank=True, null=True)
    voice = models.ForeignKey(Voice, on_delete=models.CASCADE, blank=True, null=True)
    date = models.DateTimeField()
    additional_info = models.JSONField(blank=True, null=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    bot_platform = models.ForeignKey(BotPlatform, on_delete=models.CASCADE, null=True)
    reply_markup = models.JSONField(blank=True, null=True)
    parse_mode = models.CharField(max_length=10, blank=True, null=True)  # New Field

    class Meta:
        unique_together = ["message_id", "date", "bot_platform"]

    def __str__(self):
        return f"Message {self.message_id} on {self.bot_platform.platform}"


#'photo': [{'file_id': 'AgACAgQAAxkDAAIB5mSZurrIcrYEOXALxkk0viVCyZwOAALzsDEbwzTNUFY-ASOyPRcbAQADAgADcwADLwQ', 'file_unique_id': 'AQAD87AxG8M0zVB4', 'file_size': 1590, 'width': 76, 'height': 90}, {'file_id': 'AgACAgQAAxkDAAIB5mSZurrIcrYEOXALxkk0viVCyZwOAALzsDEbwzTNUFY-ASOyPRcbAQADAgADbQADLwQ', 'file_unique_id': 'AQAD87AxG8M0zVBy', 'file_size': 23957, 'width': 271, 'height': 320}, {'file_id': 'AgACAgQAAxkDAAIB5mSZurrIcrYEOXALxkk0viVCyZwOAALzsDEbwzTNUFY-ASOyPRcbAQADAgADeAADLwQ', 'file_unique_id': 'AQAD87AxG8M0zVB9', 'file_size': 72396, 'width': 542, 'height': 640}]
class PhotoMessage(models.Model):
    message = models.ForeignKey(Message, on_delete=models.CASCADE)
    caption = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["-message__date"]

    def __str__(self):
        return f"Photo Message {self.message.message_id} on {self.message.bot_platform.platform}"


class TelegramPhoto(models.Model):
    photo_message = models.ForeignKey(PhotoMessage, on_delete=models.CASCADE)
    file_id = models.CharField(max_length=100, null=True)
    file_unique_id = models.CharField(max_length=100, null=True)
    file_size = models.IntegerField(null=True)
    width = models.IntegerField(null=True)
    height = models.IntegerField(null=True)


class Advertisement(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    messages = models.ManyToManyField(Message)

    def __str__(self):
        return f"Advertisement {self.pk}"
