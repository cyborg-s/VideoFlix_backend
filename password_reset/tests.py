import pytest
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import PasswordResetTokenGenerator

from .api.functions import send_password_reset_email


User = get_user_model()


class PasswordResetTests(APITestCase):
    """
    Test suite for password reset functionality including request and confirmation endpoints.
    """

    def setUp(self):
        """
        Creates active and inactive test users and sets URLs for password reset request and confirmation.
        """
        self.user = User.objects.create_user(
            email="testuser@example.com",
            password="TestPass123!",
            is_active=True
        )
        self.inactive_user = User.objects.create_user(
            email="inactive@example.com",
            password="TestPass123!",
            is_active=False
        )
        self.request_url = reverse('request-password-reset')
        self.confirm_url = reverse('confirm-password-reset')

    def test_request_password_reset_active_user(self):
        """
        Tests that a password reset email request for an active user returns HTTP 200 with correct detail message.
        """
        response = self.client.post(self.request_url, data={
                                    "email": self.user.email})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("Folge dem Link", response.data.get("detail", ""))

    def test_request_password_reset_inactive_user(self):
        """
        Tests that a password reset request for an inactive user returns HTTP 200 but does not send an email.
        """
        response = self.client.post(self.request_url, data={
                                    "email": self.inactive_user.email})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_request_password_reset_no_email(self):
        """
        Tests that a password reset request with an empty email returns HTTP 200 without error.
        """
        response = self.client.post(self.request_url, data={"email": ""})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_confirm_password_reset_success(self):
        """
        Tests successful password reset confirmation with valid uid, token and matching new passwords.
        """
        token_generator = PasswordResetTokenGenerator()
        token = token_generator.make_token(self.user)
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))

        data = {
            "uid": uid,
            "token": token,
            "new_password": "NewStrongPass1!",
            "new_password_confirm": "NewStrongPass1!",
        }
        response = self.client.post(self.confirm_url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("Passwort wurde erfolgreich geändert.",
                      response.data.get("detail", ""))
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("NewStrongPass1!"))

    def test_confirm_password_reset_password_mismatch(self):
        """
        Tests password reset confirmation failure when new_password and new_password_confirm do not match.
        """
        token_generator = PasswordResetTokenGenerator()
        token = token_generator.make_token(self.user)
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))

        data = {
            "uid": uid,
            "token": token,
            "new_password": "NewPass1!",
            "new_password_confirm": "MismatchPass!",
        }
        response = self.client.post(self.confirm_url, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Passwörter stimmen nicht überein", str(response.data))

    def test_confirm_password_reset_invalid_uid(self):
        """
        Tests password reset confirmation failure with invalid UID.
        """
        data = {
            "uid": "invaliduid",
            "token": "some-token",
            "new_password": "NewPass1!",
            "new_password_confirm": "NewPass1!",
        }
        response = self.client.post(self.confirm_url, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Ungültiger Link", str(response.data))

    def test_confirm_password_reset_invalid_token(self):
        """
        Tests password reset confirmation failure with invalid or expired token.
        """
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        data = {
            "uid": uid,
            "token": "invalidtoken",
            "new_password": "NewPass1!",
            "new_password_confirm": "NewPass1!",
        }
        response = self.client.post(self.confirm_url, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Ungültiger oder abgelaufener Token", str(response.data))


@pytest.mark.django_db
def test_send_password_reset_email_no_email(caplog):
    """
    Tests that sending a password reset email with no email logs a warning.
    """
    send_password_reset_email(None, None)
    assert "Keine E-Mail angegeben." in caplog.text


@pytest.mark.django_db
def test_send_password_reset_email_user_does_not_exist(caplog):
    """
    Tests that sending a password reset email for a non-existing user logs a warning.
    """
    send_password_reset_email("doesnotexist@example.com", None)
    assert "Kein Benutzer gefunden" in caplog.text


@pytest.mark.django_db
def test_send_password_reset_email_user_not_active(caplog):
    """
    Tests that sending a password reset email for an inactive user logs a warning.
    """
    user = User.objects.create(email="inactive2@example.com", is_active=False)
    send_password_reset_email(user.email, None)
    assert "Benutzer nicht aktiv" in caplog.text
