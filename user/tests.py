from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()


class UserModelTests(TestCase):

    def test_create_user_successful(self):
        email = 'testuser@example.com'
        password = 'testpass123'
        user = User.objects.create_user(email=email, password=password)
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertFalse(user.is_active)

    def test_create_user_username_auto_set(self):
        email = 'myuser@example.com'
        user = User.objects.create_user(email=email, password='pass')
        self.assertEqual(user.username, 'myuser__at__example.com')

    def test_create_user_without_email_raises_error(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(email=None, password='pass')

    def test_create_superuser_successful(self):
        email = 'admin@example.com'
        password = 'adminpass'
        user = User.objects.create_superuser(email=email, password=password)
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_active)

    def test_create_superuser_without_is_staff_raises_error(self):
        with self.assertRaises(ValueError):
            User.objects.create_superuser(
                email='admin@example.com', password='pass', is_staff=False)

    def test_create_superuser_without_is_superuser_raises_error(self):
        with self.assertRaises(ValueError):
            User.objects.create_superuser(
                email='admin@example.com', password='pass', is_superuser=False)

    def test_str_method_returns_email(self):
        user = User.objects.create_user(
            email='strtest@example.com', password='pass')
        self.assertEqual(str(user), 'strtest@example.com')

    def test_username_max_length(self):
        username = 'u' * 151
        with self.assertRaises(ValidationError):
            user = User(username=username, email='a@b.com')
            user.full_clean()

    def test_required_fields(self):
        user = User(username='testuser')
        with self.assertRaises(ValidationError):
            user.full_clean()

        user = User(email='test2@example.com')
        with self.assertRaises(ValidationError):
            user.full_clean()
