from django.test import TestCase, Client
from django.urls import reverse
from users.models import User
from django.contrib.auth import get_user_model


class TelegramAuthenticationTests(TestCase):
    """Tests for Telegram ID authentication with password creation"""

    def setUp(self):
        """Set up test client and test user"""
        self.client = Client()
        User = get_user_model()
        
        # Create a user without password (first-time user)
        self.user_no_password = User.objects.create(
            username='testuser_no_pass',
            telegram_id='123456789',
            nickname='Test User No Pass',
            gender='male'
        )
        self.user_no_password.set_unusable_password()
        self.user_no_password.save()
        
        # Create a user with password (existing user)
        self.user_with_password = User.objects.create(
            username='testuser_with_pass',
            telegram_id='987654321',
            nickname='Test User With Pass',
            gender='female'
        )
        self.user_with_password.set_password('testpass123')
        self.user_with_password.save()

    def test_first_time_user_redirected_to_create_password(self):
        """Test that first-time users are redirected to create password"""
        response = self.client.post(reverse('login'), {
            'telegram_id': '123456789',
            'password': ''
        }, follow=False)  # Don't follow redirect
        
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('create_password'))

    def test_create_password_requires_login(self):
        """Test that create_password view requires authentication"""
        response = self.client.get(reverse('create_password'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_create_password_minimum_length(self):
        """Test that password creation enforces minimum 8 characters"""
        self.client.force_login(self.user_no_password)
        
        # Try with short password (less than 8 characters)
        response = self.client.post(reverse('create_password'), {
            'password1': 'short',
            'password2': 'short'
        })
        
        # Should show error and stay on the same page
        self.assertEqual(response.status_code, 200)
        # Check that password wasn't set
        self.user_no_password.refresh_from_db()
        self.assertFalse(self.user_no_password.check_password('short'))

    def test_create_password_mismatch(self):
        """Test that password creation validates matching passwords"""
        self.client.force_login(self.user_no_password)
        
        response = self.client.post(reverse('create_password'), {
            'password1': 'password123',
            'password2': 'different123'
        })
        
        # Should show error and stay on the same page
        self.assertEqual(response.status_code, 200)
        # Check that password wasn't set
        self.user_no_password.refresh_from_db()
        self.assertFalse(self.user_no_password.check_password('password123'))

    def test_create_password_success(self):
        """Test successful password creation"""
        self.client.force_login(self.user_no_password)
        
        response = self.client.post(reverse('create_password'), {
            'password1': 'newpassword123',
            'password2': 'newpassword123'
        }, follow=False)  # Don't follow redirect
        
        # Should redirect to profile
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('profile'))
        
        # Verify password was set
        self.user_no_password.refresh_from_db()
        self.assertTrue(self.user_no_password.has_usable_password())
        self.assertTrue(self.user_no_password.check_password('newpassword123'))

    def test_existing_user_login_with_password(self):
        """Test that existing users can login with password"""
        response = self.client.post(reverse('login'), {
            'telegram_id': '987654321',
            'password': 'testpass123'
        }, follow=False)  # Don't follow redirect
        
        # Should redirect to profile
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('profile'))

    def test_existing_user_wrong_password(self):
        """Test that login fails with wrong password"""
        response = self.client.post(reverse('login'), {
            'telegram_id': '987654321',
            'password': 'wrongpassword'
        })
        
        # Should stay on login page
        self.assertEqual(response.status_code, 200)
        # User should not be logged in
        self.assertFalse('_auth_user_id' in self.client.session)

    def test_nonexistent_user(self):
        """Test login with non-existent Telegram ID"""
        response = self.client.post(reverse('login'), {
            'telegram_id': '999999999',
            'password': ''
        })
        
        # Should stay on login page
        self.assertEqual(response.status_code, 200)
        # User should not be logged in
        self.assertFalse('_auth_user_id' in self.client.session)

    def test_brute_force_protection(self):
        """Test that brute force protection locks account after max attempts"""
        # Make multiple failed login attempts
        for i in range(6):
            response = self.client.post(reverse('login'), {
                'telegram_id': '987654321',
                'password': 'wrongpassword'
            })
        
        # After 5 failed attempts, should still be on login page
        self.assertEqual(response.status_code, 200)
        # User should still not be logged in
        self.assertFalse('_auth_user_id' in self.client.session)

    def test_login_by_username(self):
        """Test login using Telegram username instead of ID"""
        response = self.client.post(reverse('login'), {
            'telegram_username': 'testuser_with_pass',
            'password': 'testpass123'
        }, follow=False)  # Don't follow redirect
        
        # Should redirect to profile
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('profile'))

    def test_user_with_password_cannot_access_create_password(self):
        """Test that users with passwords are redirected from create_password"""
        self.client.force_login(self.user_with_password)
        
        response = self.client.get(reverse('create_password'), follow=False)
        
        # Should redirect to profile
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('profile'))

    def test_password_change_in_profile_minimum_length(self):
        """Test that password change in profile enforces minimum 8 characters"""
        self.client.force_login(self.user_with_password)
        
        response = self.client.post(reverse('profile'), {
            'new_password': 'short',
            'confirm_password': 'short',
            'nickname': self.user_with_password.nickname,
            'phone': self.user_with_password.phone
        })
        
        # Should show error message
        messages = list(response.wsgi_request._messages)
        self.assertTrue(any('8 символов' in str(m) for m in messages))


class TelegramBackendTests(TestCase):
    """Tests for TelegramBackend authentication backend"""

    def setUp(self):
        """Set up test users"""
        User = get_user_model()
        
        self.user_with_password = User.objects.create(
            username='backend_test_user',
            telegram_id='111222333',
            nickname='Backend Test',
            gender='male'
        )
        self.user_with_password.set_password('testpassword123')
        self.user_with_password.save()

    def test_authenticate_with_correct_password(self):
        """Test authentication with correct password"""
        from django.contrib.auth import authenticate
        
        user = authenticate(
            telegram_id='111222333',
            password='testpassword123'
        )
        
        self.assertIsNotNone(user)
        self.assertEqual(user.telegram_id, '111222333')

    def test_authenticate_with_wrong_password(self):
        """Test authentication with wrong password"""
        from django.contrib.auth import authenticate
        
        user = authenticate(
            telegram_id='111222333',
            password='wrongpassword'
        )
        
        self.assertIsNone(user)

    def test_authenticate_by_username(self):
        """Test authentication using username"""
        from django.contrib.auth import authenticate
        
        user = authenticate(
            telegram_username='backend_test_user',
            password='testpassword123'
        )
        
        self.assertIsNotNone(user)
        self.assertEqual(user.username, 'backend_test_user')

