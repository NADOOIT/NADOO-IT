# Generated by Django 4.1.3 on 2023-04-17 15:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("nadooit_website", "0029_rename_plugin_name_plugin_name_and_more"),
    ]

    operations = [
        migrations.RenameField(
            model_name="plugin",
            old_name="plugin_html",
            new_name="html",
        ),
        migrations.RenameField(
            model_name="section",
            old_name="section_html",
            new_name="html",
        ),
    ]
