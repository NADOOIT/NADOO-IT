# Generated by Django 4.1.2 on 2022-11-04 14:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nadooit_hr', '0009_remove_employee_customers_the_employee_works_for'),
    ]

    operations = [
        migrations.AddField(
            model_name='employeecontract',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='employeemanager',
            name='can_add_new_employees',
            field=models.BooleanField(default=False),
        ),
    ]
