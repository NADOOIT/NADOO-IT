# Generated by Django 4.0.7 on 2022-08-26 15:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('nadooit_program_ownership_system', '0001_initial'),
        ('nadooit_api_executions_system', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='customerprogramexecution',
            name='customer_program',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='nadooit_program_ownership_system.nadooitcustomerprogram'),
        ),
    ]