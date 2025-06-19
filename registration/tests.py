from django.urls import reverse
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from unittest.mock import patch
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from .api.serializers import RegisterSerializer

User = get_user_model()

class RegistrationActivationTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('register')

    @patch('registration.api.functions.EmailMultiAlternatives.send')  # Patch send_mail, damit kein echter Mailversand stattfindet
    def test_register_user_success(self, mock_send_mail):
        data = {
            "email": "testuser@example.com",
            "password": "StrongPass123!",
            "password2": "StrongPass123!"
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, 201)
        self.assertIn("Please confirm your email address.", response.data["message"])

        # User existiert in DB, aber ist inactive
        user = User.objects.get(email="testuser@example.com")
        self.assertFalse(user.is_active)

        # send_mail wurde aufgerufen
        self.assertTrue(mock_send_mail.called)

    def test_register_password_mismatch(self):
        data = {
            "email": "testuser@example.com",
            "password": "pass1",
            "password2": "pass2"
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, 400)
        self.assertIn("Bitte überprüfe deine Eingaben und versuche es erneut.", response.data)

    def test_register_missing_email(self):
        data = {
            "password": "StrongPass123!",
            "password2": "StrongPass123!"
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, 400)
        self.assertIn("Bitte überprüfe deine Eingaben und versuche es erneut.", response.data)

    def test_register_username_is_read_only(self):
        data = {
            "email": "testuser2@example.com",
            "password": "StrongPass123!",
            "password2": "StrongPass123!",
            "username": "shouldnotaccept"
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, 201)
        user = User.objects.get(email="testuser2@example.com")
        self.assertNotEqual(user.username, "shouldnotaccept")  # username wird nicht aus input genommen

    def test_activate_account_success(self):
        # User anlegen und Token generieren
        user = User.objects.create_user(email='activate@example.com', password='pass')
        user.is_active = False
        user.save()

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        activate_url = reverse('activate', kwargs={'uidb64': uid, 'token': token})
        response = self.client.get(activate_url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Account activated successfully", response.data["message"])

        # User ist jetzt aktiv
        user.refresh_from_db()
        self.assertTrue(user.is_active)

    def test_activate_account_already_active(self):
        user = User.objects.create_user(email='active@example.com', password='pass')
        user.is_active = True
        user.save()

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        activate_url = reverse('activate', kwargs={'uidb64': uid, 'token': token})
        response = self.client.get(activate_url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Bitte überprüfe deine Eingaben und versuche es erneut.", response.data["message"])

    def test_activate_account_invalid_uid(self):
        activate_url = reverse('activate', kwargs={'uidb64': 'invaliduid', 'token': 'sometoken'})
        response = self.client.get(activate_url)
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid or expired activation link", response.data["message"])

    def test_activate_account_invalid_token(self):
        user = User.objects.create_user(email='badtoken@example.com', password='pass')
        user.is_active = False
        user.save()

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        bad_token = 'wrongtoken'

        activate_url = reverse('activate', kwargs={'uidb64': uid, 'token': bad_token})
        response = self.client.get(activate_url)
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid or expired activation link", response.data["message"])

    def test_password_mismatch(self):
        data = {
            "email": "test2@example.com",
            "password": "TestPass123!",
            "password2": "DifferentPass123!",
        }
        serializer = RegisterSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("password", serializer.errors)
        self.assertEqual(serializer.errors["password"][0], "Passwords do not match.")
