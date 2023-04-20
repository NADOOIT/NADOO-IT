from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("nadooit_website", "0023_remove_session_session_signals"),
    ]

    operations = [
        migrations.AddField(
            model_name="session_signals",
            name="session",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="nadooit_website.session",
            ),
        ),
    ]
