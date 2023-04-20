# Generated by Django 4.1.3 on 2023-04-15 16:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("nadooit_website", "0021_category_remove_section_category_section_categories"),
    ]

    operations = [
        migrations.AddField(
            model_name="session",
            name="experiment_group",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="nadooit_website.experimentgroup",
            ),
        ),
    ]
