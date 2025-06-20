from django.urls import reverse 
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.authtoken.models import Token

User = get_user_model()


class LoginTests(APITestCase):
    """
    Test suite for the Login API endpoint.
    Covers various scenarios including successful login, 
    invalid credentials, and inactive users.
    """

    def setUp(self):
        """
        Set up test users and the login URL before each test.
        """
        self.user = User.objects.create_user(
            email='testuser@example.com',
            password='StrongPass123!',
            username='testuser',
            is_active=True
        )
        self.login_url = reverse('login:login')
        print("Login URL is:", self.login_url)

        self.inactive_user = User.objects.create_user(
            email='inactive@example.com',
            password='StrongPass123!',
            username='inactiveuser',
            is_active=False
        )

    def test_login_success(self):
        """
        Test login with correct credentials.
        Ensures token and user details are returned upon success.
        """
        data = {
            'email': 'testuser@example.com',
            'password': 'StrongPass123!'
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
        self.assertEqual(response.data['email'], self.user.email)
        self.assertEqual(response.data['user_id'], self.user.id)

        token = Token.objects.filter(user=self.user).first()
        self.assertIsNotNone(token)
        self.assertEqual(response.data['token'], token.key)

    def test_login_invalid_password(self):
        """
        Test login with incorrect password.
        Expects a 400 Bad Request with appropriate error message.
        """
        data = {
            'email': 'testuser@example.com',
            'password': 'WrongPassword'
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', response.data)
        self.assertIn('Invalid credentials', str(response.data))

    def test_login_invalid_email(self):
        """
        Test login with non-existent email.
        Expects a 400 Bad Request with appropriate error message.
        """
        data = {
            'email': 'nonexistent@example.com',
            'password': 'AnyPass123!'
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', response.data)
        self.assertIn('Invalid credentials', str(response.data))

    def test_login_inactive_user(self):
        """
        Test login with an inactive user account.
        Expects a 400 Bad Request with email confirmation error.
        """
        data = {
            'email': 'inactive@example.com',
            'password': 'StrongPass123!'
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertIn('non_field_errors', response.data)
        self.assertIn('Email not confirmed.',
                      response.data['non_field_errors'])
