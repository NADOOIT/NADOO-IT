# Generated by Django 4.1.9 on 2023-06-12 19:31

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('bot_management', '0005_apikey_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='botplatform',
            name='secret_token',
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
    ]