#!/bin/sh

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate

# Create superuser if it doesn't exist
echo "Creating superuser if it doesn't exist..."
python -c "
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nadooit.settings')
import django
django.setup()
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', '123456')
    print('Superuser created successfully')
else:
    print('Superuser already exists')
"

# Start server
echo "Starting server..."
python manage.py runserver 0.0.0.0:8000
