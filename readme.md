This is the nadooit execution manegment system. It records exectutions by customers

To deploy:

Change line 20-24 in settings.py to the production config.json file

Set ~Line 35 
//# SECURITY WARNING: don't run with debug turned on in production!
//DEBUG = True
to False


make sure that the directory/configfile exists that is shown when using

python
>>>from pathlib import Path
>>>Path.home().joinpath('NADOOIT').joinpath('config').joinpath('config.json')

set the current directory to the packagedir (managmentsystem)

first to create the required models run
python manage.py migrate

if this is the inisial setup a superuser needs to created.
To create it use:
python manage.py createsuperuser
