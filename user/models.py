from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone


class UserManager(BaseUserManager):
    """
    Custom user manager to handle user creation with email as unique identifier.
    """

    def create_user(self, email, username=None, password=None, **extra_fields):
        """
        Create and save a regular user with the given email and password.

        Args:
            email (str): User's email address.
            username (str, optional): User's username. Defaults to modified email if not provided.
            password (str, optional): User's password.
            **extra_fields: Additional fields for the user model.

        Raises:
            ValueError: If email is not provided.

        Returns:
            User: Newly created user instance.
        """
        if not email:
            raise ValueError('Email must be provided')
        email = self.normalize_email(email)

        if not username:
            username = email.replace('@', '__at__')

        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username=None, password=None, **extra_fields):
        """
        Create and save a superuser with the given email and password.

        Args:
            email (str): User's email address.
            username (str, optional): User's username. Defaults to modified email if not provided.
            password (str): User's password.
            **extra_fields: Additional fields for the user model.

        Raises:
            ValueError: If is_staff or is_superuser flags are not True.

        Returns:
            User: Newly created superuser instance.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        if not username:
            username = email.replace('@', '__at__')

        return self.create_user(email, username=username, password=password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model where username and email are unique identifiers.

    Attributes:
        username (str): Unique username.
        email (str): Unique email address.
        first_name (str): Optional first name.
        last_name (str): Optional last name.
        is_active (bool): Designates whether this user should be treated as active.
        is_staff (bool): Designates whether the user can log into the admin site.
        date_joined (datetime): Timestamp of when the user joined.
    """
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        """
        Return string representation of the user.

        Returns:
            str: Email address of the user.
        """
        return self.email
