# Generated by Django 4.1.2 on 2022-11-01 16:03

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("nadooit_hr", "0007_employeecontract"),
    ]

    operations = [
        migrations.AddField(
            model_name="employee",
            name="created_at",
            field=models.DateTimeField(
                auto_now_add=True, default=django.utils.timezone.now
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="employee",
            name="updated_at",
            field=models.DateTimeField(auto_now=True),
        ),
    ]
