# Generated by Django 4.1.3 on 2023-04-24 16:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("nadooit_website", "0033_video_section_video"),
    ]

    operations = [
        migrations.RenameField(
            model_name="video",
            old_name="video_id",
            new_name="id",
        ),
    ]
