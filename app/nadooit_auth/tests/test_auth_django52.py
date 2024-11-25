"""
Tests for authentication system compatibility with Django 5.2
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from nadooit_auth.models import User

class AuthenticationDjango52Test(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

    def test_password_validation(self):
        """Test Django 5.2's password validation"""
        # Test weak password
        with self.assertRaises(ValidationError):
            User.objects.create_user(
                username='weakpass',
                password='123'
            )

    def test_session_authentication(self):
        """Test session-based authentication"""
        login_successful = self.client.login(
            username='testuser',
            password='testpass123'
        )
        self.assertTrue(login_successful)
        
        response = self.client.get(reverse('admin:index'))
        self.assertEqual(response.status_code, 200)

    def test_logout_behavior(self):
        """Test logout behavior in Django 5.2"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('admin:logout'))
        self.assertEqual(response.status_code, 200)
        
        # Verify user is logged out
        response = self.client.get(reverse('admin:index'))
        self.assertNotEqual(response.status_code, 200)

    def test_password_reset(self):
        """Test password reset functionality"""
        response = self.client.get(reverse('admin:password_reset'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/password_reset_form.html')

class CustomUserCodeAuthBackendTest(TestCase):
    """Test the custom user code authentication backend"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

    def test_custom_auth_backend(self):
        """Test custom authentication backend compatibility"""
        from nadooit_auth.custom_user_code_auth_backend import UserCodeBackend
        
        backend = UserCodeBackend()
        authenticated_user = backend.authenticate(
            request=None,
            username='testuser',
            password='testpass123'
        )
        self.assertIsNotNone(authenticated_user)
        self.assertEqual(authenticated_user, self.user)

    def test_invalid_auth_attempt(self):
        """Test invalid authentication attempt"""
        from nadooit_auth.custom_user_code_auth_backend import UserCodeBackend
        
        backend = UserCodeBackend()
        authenticated_user = backend.authenticate(
            request=None,
            username='testuser',
            password='wrongpass'
        )
        self.assertIsNone(authenticated_user)

class SecurityFeaturesDjango52Test(TestCase):
    """Test Django 5.2 security features"""

    def setUp(self):
        self.client = Client()

    def test_password_hashers(self):
        """Test password hashing configuration"""
        from django.conf import settings
        
        self.assertTrue(hasattr(settings, 'PASSWORD_HASHERS'))
        # Verify default hasher is secure
        self.assertEqual(
            settings.PASSWORD_HASHERS[0],
            'django.contrib.auth.hashers.PBKDF2PasswordHasher'
        )

    def test_session_security(self):
        """Test session security settings"""
        from django.conf import settings
        
        # Verify secure session configuration
        self.assertTrue(settings.SESSION_COOKIE_SECURE)
        self.assertTrue(settings.CSRF_COOKIE_SECURE)
        self.assertTrue(settings.CSRF_USE_SESSIONS)

class UserModelDjango52Test(TestCase):
    """Test User model compatibility with Django 5.2"""

    def test_user_creation(self):
        """Test user creation with new Django 5.2 features"""
        user = User.objects.create_user(
            username='newuser',
            password='securepass123'
        )
        self.assertIsNotNone(user.pk)
        self.assertTrue(user.check_password('securepass123'))

    def test_user_permissions(self):
        """Test user permissions system"""
        user = User.objects.create_user(
            username='permuser',
            password='testpass123',
            is_staff=True
        )
        
        # Test permission assignment
        from django.contrib.auth.models import Permission
        from django.contrib.contenttypes.models import ContentType
        
        content_type = ContentType.objects.get_for_model(User)
        permission = Permission.objects.get(
            codename='add_user',
            content_type=content_type,
        )
        
        user.user_permissions.add(permission)
        self.assertTrue(user.has_perm('auth.add_user'))
