from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from rest_framework import status


class JWTAuthTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@test.com'
        )
        self.login_url = '/api/v1/auth/token/'
        self.refresh_url = '/api/v1/auth/token/refresh/'
        self.movies_url = '/api/v1/movies/'

    def test_jwt_token_obtain(self):
        """Test: JWT Token erhalten"""
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_jwt_token_invalid_credentials(self):
        """Test: Falsche Logindaten"""
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'falsch'
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_access_protected_endpoint_with_jwt(self):
        """Test: Geschützten Endpoint mit Token aufrufen"""
        # Erst Token holen
        token_response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'testpass123'
        })
        access_token = token_response.data['access']

        # Dann mit Token auf geschützten Endpoint zugreifen
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = self.client.get(self.movies_url)

        self.assertNotEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_jwt_token_refresh(self):
        """Test: Token refreshen"""
        # Erst Token holen
        token_response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'testpass123'
        })
        refresh_token = token_response.data['refresh']

        # Token refreshen
        response = self.client.post(self.refresh_url, {
            'refresh': refresh_token
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)