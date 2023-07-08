from django.db import migrations


def drop_bot_management_tables(apps, schema_editor):
    with schema_editor.connection.cursor() as cursor:
        cursor.execute("DROP TABLE IF EXISTS bot_management_* CASCADE;")


class Migration(migrations.Migration):
    dependencies = []

    operations = [
        migrations.RunPython(drop_bot_management_tables),
    ]
