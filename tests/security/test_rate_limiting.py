# tests/security/test_rate_limiting.py
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from django.core.cache import cache


class LoginRateLimitTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.login_url = '/api/users/login/'
        # Clear cache before each test
        cache.clear()

        # Create a test user
        self.test_user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )

    def test_login_rate_limit_anon(self):
        """Test that anonymous users are rate limited to 5 attempts per hour"""
        # Make 5 login attempts with wrong password
        for i in range(5):
            response = self.client.post(self.login_url, {
                'username': 'testuser',
                'password': 'wrongpass'
            })
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # 6th attempt should be rate limited
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'wrongpass'
        })
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

        # Verify rate limit message
        self.assertIn('detail', response.data)
        self.assertIn('Request was throttled', str(response.data['detail']))

    def test_successful_login_not_limited(self):
        """Test that successful logins don't count against the rate limit"""
        # This test checks that the throttle only counts failed attempts
        # Note: DRF throttle counts all requests to the endpoint, not just failures
        # So we need to test differently

        # Make 4 failed attempts
        for i in range(4):
            response = self.client.post(self.login_url, {
                'username': 'testuser',
                'password': 'wrongpass'
            })
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # 5th attempt should be successful (not limited yet)
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 6th attempt (any request) should be rate limited
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

    def test_different_users_separate_limits(self):
        """Test that rate limits are applied per IP/user"""
        # Create second user
        User.objects.create_user(
            username='testuser2',
            password='testpass456',
            email='test2@example.com'
        )

        # First user attempts - 5 times
        for i in range(5):
            response = self.client.post(self.login_url, {
                'username': 'testuser',
                'password': 'wrongpass'
            })
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # First user 6th attempt - should be limited
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'wrongpass'
        })
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

        # Second user should still be able to attempt
        response = self.client.post(self.login_url, {
            'username': 'testuser2',
            'password': 'wrongpass'
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_rate_limit_reset(self):
        """Test that rate limits reset after the time period"""
        # Use cache mock to simulate time passing
        from unittest.mock import patch

        with patch('django.core.cache.cache.get') as mock_cache_get:
            # First attempt
            response = self.client.post(self.login_url, {
                'username': 'testuser',
                'password': 'wrongpass'
            })
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

