# Generated by Django 4.1.3 on 2023-04-07 16:08

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ("nadooit_website", "0012_session_signals_session_session_signals"),
    ]

    operations = [
        migrations.CreateModel(
            name="Question_Answer",
            fields=[
                (
                    "question_answer_id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("question_answer_date", models.DateTimeField(auto_now_add=True)),
                ("question_answer_question", models.TextField(blank=True)),
                ("question_answer_answer", models.TextField(blank=True)),
            ],
        ),
    ]