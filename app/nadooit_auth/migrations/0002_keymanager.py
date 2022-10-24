# Generated by Django 4.1.2 on 2022-10-24 11:54

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('nadooit_auth', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='KeyManager',
            fields=[
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('can_create_keys', models.BooleanField(default=False)),
                ('can_delete_keys', models.BooleanField(default=False)),
                ('can_update_keys', models.BooleanField(default=False)),
                ('can_create_key_managers', models.BooleanField(default=False)),
                ('can_delete_key_managers', models.BooleanField(default=False)),
                ('can_update_key_managers', models.BooleanField(default=False)),
            ],
        ),
    ]
