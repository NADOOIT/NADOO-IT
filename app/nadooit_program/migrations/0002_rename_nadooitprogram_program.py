# Generated by Django 4.1.2 on 2022-10-31 16:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nadooit_program_ownership_system', '0010_rename_nadooitprogramshare_programshare'),
        ('nadooit_workflow', '0001_initial'),
        ('nadooit_program', '0001_initial'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='NadooitProgram',
            new_name='Program',
        ),
    ]