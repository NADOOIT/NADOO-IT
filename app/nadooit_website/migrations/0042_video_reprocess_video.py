# Generated by Django 4.1.9 on 2023-06-02 10:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nadooit_website', '0041_alter_session_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='video',
            name='reprocess_video',
            field=models.BooleanField(default=False),
        ),
    ]
