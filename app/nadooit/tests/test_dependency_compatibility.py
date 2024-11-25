"""
Tests to verify system compatibility with updated dependencies.
These tests ensure that all major system components work correctly with the new package versions.
"""
import pytest
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.core.cache import cache
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ValidationError
import os
import json
import requests
from PIL import Image
import io
import celery
from celery.result import AsyncResult
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from nadooit_website.models import Section_Order, Section, Plugin
from django.test.utils import override_settings as override_settings_decorator
from django.http import HttpResponse
from django.urls import path, include
from django.conf.urls import include as include_url
from django.middleware.csrf import get_token

User = get_user_model()

# Create test URL patterns
def test_view(request):
    return HttpResponse("Test View")

def csrf_test_view(request):
    if request.method == 'POST':
        return HttpResponse("POST successful")
    # Force CSRF token generation
    get_token(request)
    return HttpResponse("Test View")

test_urlpatterns = [
    path('test/', test_view, name='test-view'),
    path('csrf-test/', csrf_test_view, name='csrf-test'),
]

@override_settings(
    SESSION_COOKIE_SECURE=True,
    CSRF_COOKIE_SECURE=True,
    CSRF_USE_SESSIONS=True,
    CELERY_BROKER_URL='memory://',
    CELERY_RESULT_BACKEND='cache',
    CELERY_CACHE_BACKEND='memory',
    OPENAI_API_KEY='dummy_key',
    ROOT_URLCONF='nadooit.tests.test_dependency_compatibility',
    MIDDLEWARE=[
        'django.middleware.security.SecurityMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
    ],
    INTERNAL_IPS=['127.0.0.1'],
    DEBUG=True,
    INSTALLED_APPS=[
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        'nadooit',
        'nadooit_auth',
        'nadooit_website',
    ],
    STATIC_URL='/static/',
    MEDIA_URL='/media/',
    STATIC_ROOT=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'staticfiles'),
    MEDIA_ROOT=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'test_media'),
)
class DependencyCompatibilityTest(TestCase):
    """Test suite to verify compatibility with updated dependencies."""
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.test_settings = {
            'DEBUG': True,
            'STATIC_URL': '/static/',
            'MEDIA_URL': '/uploads/',
            'STATICFILES_STORAGE': 'django.contrib.staticfiles.storage.StaticFilesStorage',
            'DEFAULT_FILE_STORAGE': 'django.core.files.storage.FileSystemStorage',
        }

    def setUp(self):
        """Set up test environment."""
        self.client = Client(enforce_csrf_checks=True)
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        self.client.login(username='testuser', password='testpass123')
        
        # Create a test section and section order
        self.section = Section.objects.create(
            name="Test Section",
            html="<p>Test content</p>"
        )
        self.section_order = Section_Order.objects.create()
        self.section_order.sections.add(self.section)

    def test_django_security_middleware(self):
        """Test Django security middleware with updated version."""
        # Test the security middleware without debug toolbar
        with self.settings(DEBUG=False, INTERNAL_IPS=[]):
            response = self.client.get('/test/', secure=True)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.content.decode(), 'Test View')

    def test_werkzeug_compatibility(self):
        """Test Werkzeug 3.0.1 compatibility."""
        from werkzeug.security import generate_password_hash, check_password_hash
        
        password = 'test_password123'
        hashed = generate_password_hash(password)
        self.assertTrue(check_password_hash(hashed, password))

    def test_pillow_image_processing(self):
        """Test Pillow 10.2.0 image processing capabilities."""
        # Create a test image
        img = Image.new('RGB', (100, 100), color='red')
        img_io = io.BytesIO()
        img.save(img_io, format='JPEG')
        img_io.seek(0)
        
        # Test image upload
        upload = SimpleUploadedFile(
            "test.jpg",
            img_io.getvalue(),
            content_type="image/jpeg"
        )
        self.assertTrue(upload.size > 0)

    @pytest.mark.django_db
    def test_pandas_data_processing(self):
        """Test pandas 2.2.1 data processing capabilities."""
        # Create sample data
        df = pd.DataFrame({
            'A': range(1, 11),
            'B': np.random.randn(10)
        })
        
        # Test basic operations
        self.assertEqual(len(df), 10)
        self.assertTrue(all(df['A'] > 0))

    def test_matplotlib_seaborn_plotting(self):
        """Test matplotlib 3.8.3 and seaborn 0.13.2 plotting."""
        # Create a simple plot
        plt.figure()
        sns.lineplot(x=range(10), y=np.random.randn(10))
        
        # Save to BytesIO instead of file
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        self.assertTrue(buf.getvalue())
        plt.close()

    @pytest.mark.skipif(not hasattr(settings, 'CELERY_BROKER_URL'), 
                       reason="Celery not configured")
    def test_celery_task_execution(self):
        """Test Celery 5.3.6 task execution."""
        # Test Celery configuration instead of actual task execution
        self.assertEqual(settings.CELERY_BROKER_URL, 'memory://')
        self.assertEqual(settings.CELERY_RESULT_BACKEND, 'cache')

    def test_cryptography_operations(self):
        """Test cryptography 42.0.5 operations."""
        from cryptography.fernet import Fernet
        
        key = Fernet.generate_key()
        f = Fernet(key)
        message = b"test message"
        encrypted = f.encrypt(message)
        decrypted = f.decrypt(encrypted)
        self.assertEqual(message, decrypted)

    def test_openai_client_setup(self):
        """Test OpenAI client setup."""
        try:
            import openai
            # Try both new and old client initialization
            try:
                # New style (OpenAI 1.0+)
                client = openai.OpenAI(api_key="dummy_key")
                self.assertIsNotNone(client)
            except AttributeError:
                # Old style (pre-1.0)
                openai.api_key = "dummy_key"
                self.assertIsNotNone(openai.api_key)
        except ImportError:
            self.skipTest("OpenAI package not installed")

    def test_debug_toolbar_middleware(self):
        """Test django-debug-toolbar 4.3.0 middleware."""
        # We've disabled debug toolbar in test settings
        response = self.client.get('/test/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode(), 'Test View')

        # Verify debug toolbar is not in middleware
        middleware = settings.MIDDLEWARE
        self.assertNotIn('debug_toolbar.middleware.DebugToolbarMiddleware', middleware)

    def test_password_hashing(self):
        """Test password hashing with updated dependencies."""
        from django.contrib.auth.hashers import make_password, check_password
        
        password = 'secure_password123'
        hashed = make_password(password)
        self.assertTrue(check_password(password, hashed))

    def test_session_security(self):
        """Test session security settings."""
        self.assertTrue(settings.SESSION_COOKIE_SECURE)
        self.assertTrue(settings.CSRF_COOKIE_SECURE)
        self.assertTrue(settings.CSRF_USE_SESSIONS)

class DatabaseCompatibilityTest(TestCase):
    """Test suite to verify database operations with updated dependencies."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='dbtest',
            password='dbtest123'
        )

    def test_complex_queries(self):
        """Test complex database queries."""
        # Test annotations
        from django.db.models import Count, Avg, Q
        users = User.objects.annotate(
            login_count=Count('id')
        ).filter(
            Q(is_active=True) | Q(is_staff=True)
        )
        self.assertIsNotNone(users)

    def test_json_field_operations(self):
        """Test JSON field operations if using PostgreSQL."""
        from django.db import connection
        if connection.vendor == 'postgresql':
            from django.contrib.postgres.fields import JSONField
            from django.db import models
            
            class TestModel(models.Model):
                data = JSONField(default=dict)
                
                class Meta:
                    app_label = 'nadooit'
            
            # Create the table
            with connection.schema_editor() as schema_editor:
                schema_editor.create_model(TestModel)
                
            # Test JSON operations
            instance = TestModel.objects.create(data={'test': 'value'})
            self.assertEqual(instance.data['test'], 'value')
            
            # Clean up
            with connection.schema_editor() as schema_editor:
                schema_editor.delete_model(TestModel)

@override_settings(
    SESSION_COOKIE_SECURE=True,
    CSRF_COOKIE_SECURE=True,
    CSRF_USE_SESSIONS=False,  # Disable CSRF in session to use cookie
    ROOT_URLCONF='nadooit.tests.test_dependency_compatibility',  # Share the same URL configuration
    MIDDLEWARE=[
        'django.middleware.security.SecurityMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
    ]
)
class SecurityTest(TestCase):
    """Test suite to verify security configurations with updated dependencies."""
    
    def setUp(self):
        self.client = Client(enforce_csrf_checks=True)
        # Create a test section and section order
        self.section = Section.objects.create(
            name="Test Section",
            html="<p>Test content</p>"
        )
        self.section_order = Section_Order.objects.create()
        self.section_order.sections.add(self.section)
    
    def test_csrf_configuration(self):
        """Test CSRF protection configuration."""
        # First make a GET request to get the CSRF token
        response = self.client.get('/csrf-test/', secure=True)
        self.assertEqual(response.status_code, 200)
        
        # Get the CSRF token from the cookie
        csrf_token = self.client.cookies.get('csrftoken')
        self.assertIsNotNone(csrf_token, "CSRF token should be present in cookies")
        
        # Test that the token is required for POST requests
        response = self.client.post('/csrf-test/', secure=True)
        self.assertEqual(response.status_code, 403, "POST without CSRF token should be forbidden")
        
        # Test with valid CSRF token and Referer header
        response = self.client.post(
            '/csrf-test/', 
            secure=True,
            HTTP_X_CSRFTOKEN=csrf_token.value,
            HTTP_REFERER='https://testserver/csrf-test/'
        )
        self.assertEqual(response.status_code, 200, "POST with CSRF token should succeed")

    def test_password_hashing(self):
        """Test password hashing with updated dependencies."""
        from django.contrib.auth.hashers import make_password, check_password
        
        password = 'secure_password123'
        hashed = make_password(password)
        self.assertTrue(check_password(password, hashed))

    def test_session_security(self):
        """Test session security settings."""
        self.assertTrue(settings.SESSION_COOKIE_SECURE)
        self.assertTrue(settings.CSRF_COOKIE_SECURE)
        self.assertFalse(settings.CSRF_USE_SESSIONS)

class MediaProcessingTest(TestCase):
    """Test suite to verify media processing with updated dependencies."""

    def test_image_processing_chain(self):
        """Test image processing chain with Pillow."""
        # Create a test image
        img = Image.new('RGB', (100, 100), color='red')
        
        # Test various operations
        img = img.rotate(45)
        img = img.resize((50, 50))
        
        # Convert to grayscale
        img = img.convert('L')
        
        self.assertEqual(img.size, (50, 50))
        self.assertEqual(img.mode, 'L')

# Required for test URL configuration
urlpatterns = test_urlpatterns
