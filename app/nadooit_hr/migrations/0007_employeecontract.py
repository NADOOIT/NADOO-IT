# Generated by Django 4.1.2 on 2022-11-01 15:56

import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("nadooit_crm", "0001_initial"),
        ("nadooit_hr", "0006_customermanager_can_give_customermanager_role_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="EmployeeContract",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("start_date", models.DateField(auto_now_add=True)),
                ("end_date", models.DateField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "customer",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="nadooit_crm.customer",
                    ),
                ),
                (
                    "employee",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="nadooit_hr.employee",
                    ),
                ),
            ],
        ),
    ]
