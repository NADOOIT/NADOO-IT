# Generated by Django 4.1.7 on 2023-04-04 17:11

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('nadooit_website', '0008_signals_options_section_signal_options'),
    ]

    operations = [
        migrations.CreateModel(
            name='Session_Signals',
            fields=[
                ('session_signal_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('session_signal_date', models.DateTimeField(auto_now_add=True)),
                ('session', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='nadooit_website.session')),
                ('signal', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='nadooit_website.signals_options')),
            ],
        ),
    ]