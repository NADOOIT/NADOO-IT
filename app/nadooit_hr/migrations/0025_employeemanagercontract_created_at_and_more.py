# Generated by Django 4.1.5 on 2023-01-09 18:20

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('nadooit_hr', '0024_customerprogrammanagercontract_created_at_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='employeemanagercontract',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='employeemanagercontract',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
