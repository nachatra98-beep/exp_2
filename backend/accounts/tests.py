from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status

class AuthApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = '/api/auth/register/'
        self.login_url = '/api/auth/login/'
        self.refresh_url = '/api/auth/refresh/'
        self.me_url = '/api/auth/me/'

    def test_register_user_success(self):
        data = {
            'username': 'nachatra',
            'email': 'nachatra@example.com',
            'password': 'StrongPassword123'
        }
        res = self.client.post(self.register_url, data)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertIn('access', res.data)
        self.assertIn('refresh', res.data)
        self.assertEqual(res.data['user']['username'], 'nachatra')

    def test_register_short_password_fails(self):
        data = {
            'username': 'nachatra',
            'email': 'nachatra@example.com',
            'password': 'short'
        }
        res = self.client.post(self.register_url, data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_success(self):
        User.objects.create_user(username='nachatra', email='nachatra@example.com', password='StrongPassword123')
        res = self.client.post(self.login_url, {
            'username': 'nachatra',
            'password': 'StrongPassword123'
        })
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('access', res.data)
        self.assertIn('refresh', res.data)

    def test_login_invalid_password_returns_clear_error(self):
        User.objects.create_user(username='nachatra', email='nachatra@example.com', password='StrongPassword123')
        res = self.client.post(self.login_url, {
            'username': 'nachatra',
            'password': 'WrongPassword123'
        })
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('detail', res.data)
        self.assertEqual(res.data['detail'], 'Invalid username or password.')

    def test_token_refresh(self):
        User.objects.create_user(username='nachatra', email='nachatra@example.com', password='StrongPassword123')
        login_res = self.client.post(self.login_url, {
            'username': 'nachatra',
            'password': 'StrongPassword123'
        })
        refresh_token = login_res.data['refresh']
        res = self.client.post(self.refresh_url, {'refresh': refresh_token})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('access', res.data)
