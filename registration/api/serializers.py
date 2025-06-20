from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password

from user.models import User


class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.

    Fields:
        email: User's email address.
        username: Read-only username, generated automatically.
        password: Password input, write-only and validated using Django's password validators.
        password2: Password confirmation input, write-only.

    Validation:
        Ensures that 'password' and 'password2' fields match.

    Creation:
        Creates a new user with the provided email and password.
        Sets the user as inactive initially (e.g., pending email activation).
    """

    password = serializers.CharField(
        write_only=True, validators=[validate_password]
    )
    password2 = serializers.CharField(write_only=True)
    username = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = ('email', 'username', 'password', 'password2')

    def validate(self, attrs):
        """
        Validates that both password fields match.

        Args:
            attrs (dict): The input data dictionary.

        Raises:
            serializers.ValidationError: If the two password fields do not match.

        Returns:
            dict: The validated data.
        """
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError(
                {"password": "Passwords do not match."}
            )
        return attrs

    def create(self, validated_data):
        """
        Creates a new inactive user with the given email and password.

        Args:
            validated_data (dict): The validated data from input.

        Returns:
            User: The created User instance.
        """
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
        )
        user.is_active = False
        user.save()
        return user
