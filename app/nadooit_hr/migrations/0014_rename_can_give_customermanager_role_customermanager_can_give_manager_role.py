# Generated by Django 4.1.2 on 2022-11-04 15:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nadooit_hr', '0013_rename_can_give_employeemanager_role_employeemanager_can_give_manager_role'),
    ]

    operations = [
        migrations.RenameField(
            model_name='customermanager',
            old_name='can_give_CustomerManager_role',
            new_name='can_give_manager_role',
        ),
    ]