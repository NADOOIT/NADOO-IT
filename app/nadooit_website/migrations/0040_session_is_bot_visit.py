# Generated by Django 4.1.9 on 2023-05-19 11:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nadooit_website', '0039_file_section_file'),
    ]

    operations = [
        migrations.AddField(
            model_name='session',
            name='is_bot_visit',
            field=models.BooleanField(default=False),
        ),
    ]
