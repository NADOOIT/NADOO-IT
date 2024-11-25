"""
Tests to verify custom authentication system compatibility with updated dependencies.
"""
import pytest
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.conf import settings
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.auth.middleware import AuthenticationMiddleware
from django.test.client import RequestFactory
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.messages.storage.fallback import FallbackStorage

User = get_user_model()

class AuthenticationCompatibilityTest(TestCase):
    """Test suite to verify custom authentication system compatibility."""
    
    def setUp(self):
        """Set up test environment."""
        self.client = Client()
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='authtest',
            password='authtest123',
            email='authtest@example.com'
        )
        
        # Set up the request object
        self.request = self.factory.get('/')
        middleware = SessionMiddleware(lambda x: None)
        middleware.process_request(self.request)
        self.request.session.save()
        
        # Add messages support
        messages = FallbackStorage(self.request)
        setattr(self.request, '_messages', messages)
        
        # Process the request through auth middleware
        auth_middleware = AuthenticationMiddleware(lambda x: None)
        auth_middleware.process_request(self.request)
        
        self.request.user = self.user

    def test_login_flow(self):
        """Test the complete login flow with updated dependencies."""
        # Test logout first to ensure clean state
        self.client.logout()
        
        # Test login
        response = self.client.post(reverse('login'), {
            'username': 'authtest',
            'password': 'authtest123'
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['user'].is_authenticated)

    def test_password_validation(self):
        """Test password validation with updated dependencies."""
        from django.contrib.auth.password_validation import validate_password
        
        # Test valid password
        valid_password = 'ValidPass123!'
        try:
            validate_password(valid_password, self.user)
        except ValidationError:
            self.fail("Valid password failed validation")
        
        # Test invalid password
        invalid_password = '123'
        with self.assertRaises(ValidationError):
            validate_password(invalid_password, self.user)

    def test_session_handling(self):
        """Test session handling with updated dependencies."""
        self.client.force_login(self.user)
        response = self.client.get('/')
        
        # Check session cookie
        self.assertTrue(settings.SESSION_COOKIE_NAME in response.cookies)
        self.assertTrue(response.cookies[settings.SESSION_COOKIE_NAME]['secure'])
        self.assertTrue(response.cookies[settings.SESSION_COOKIE_NAME]['httponly'])

    def test_custom_user_model(self):
        """Test custom user model compatibility."""
        # Test user creation
        new_user = User.objects.create_user(
            username='newuser',
            password='newpass123',
            email='new@example.com'
        )
        self.assertIsNotNone(new_user.pk)
        
        # Test user authentication
        self.assertTrue(
            self.client.login(username='newuser', password='newpass123')
        )

    @pytest.mark.skipif(not hasattr(settings, 'MFA_REQUIRED'), 
                       reason="MFA not configured")
    def test_mfa_compatibility(self):
        """Test MFA compatibility with updated dependencies."""
        # Test MFA setup
        response = self.client.post(reverse('mfa_setup'), {
            'method': 'totp'
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        
        # Test MFA verification
        if hasattr(self.user, 'mfa_enabled') and self.user.mfa_enabled:
            response = self.client.post(reverse('mfa_verify'), {
                'code': '123456'  # Test code
            })
            self.assertEqual(response.status_code, 302)  # Should redirect

    def test_password_reset_flow(self):
        """Test password reset flow with updated dependencies."""
        # Request password reset
        response = self.client.post(reverse('password_reset'), {
            'email': 'authtest@example.com'
        })
        self.assertEqual(response.status_code, 302)
        
        # Check if the email was queued
        from django.core import mail
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ['authtest@example.com'])

    def test_auth_backend_compatibility(self):
        """Test custom authentication backend compatibility."""
        from django.contrib.auth import authenticate
        
        # Test authentication with username
        user = authenticate(username='authtest', password='authtest123')
        self.assertIsNotNone(user)
        self.assertEqual(user.username, 'authtest')
        
        # Test authentication with email
        user = authenticate(email='authtest@example.com', password='authtest123')
        self.assertIsNotNone(user)
        self.assertEqual(user.email, 'authtest@example.com')

    def test_permission_handling(self):
        """Test permission handling with updated dependencies."""
        from django.contrib.auth.models import Permission
        from django.contrib.contenttypes.models import ContentType
        
        # Create a test permission
        content_type = ContentType.objects.get_for_model(User)
        permission = Permission.objects.create(
            codename='can_test',
            name='Can Test',
            content_type=content_type,
        )
        
        # Add permission to user
        self.user.user_permissions.add(permission)
        
        # Test permission checking
        self.assertTrue(self.user.has_perm(f'{content_type.app_label}.can_test'))

    def test_group_handling(self):
        """Test group handling with updated dependencies."""
        from django.contrib.auth.models import Group
        
        # Create test group
        group = Group.objects.create(name='TestGroup')
        
        # Add user to group
        self.user.groups.add(group)
        
        # Test group membership
        self.assertTrue(self.user.groups.filter(name='TestGroup').exists())
        
        # Test group-based permissions
        content_type = ContentType.objects.get_for_model(User)
        permission = Permission.objects.create(
            codename='can_group_test',
            name='Can Group Test',
            content_type=content_type,
        )
        group.permissions.add(permission)
        
        self.assertTrue(
            self.user.has_perm(f'{content_type.app_label}.can_group_test')
        )
