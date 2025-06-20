from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class LoginSerializer(serializers.Serializer):
    """
    Serializer for user login. Validates user credentials and checks for active status.
    """
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        """
        Validates the provided email and password.
        Ensures the user exists, the password is correct, and the account is active.
        
        Args:
            data (dict): Dictionary containing 'email' and 'password'.

        Returns:
            dict: Validated data including the authenticated user.

        Raises:
            serializers.ValidationError: If the credentials are invalid or the account is inactive.
        """
        email = data.get('email')
        password = data.get('password')

        try:
            user_obj = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                {'non_field_errors': ["Invalid credentials."]})

        if not user_obj.check_password(password):
            raise serializers.ValidationError(
                {'non_field_errors': ["Invalid credentials."]})

        if not user_obj.is_active:
            raise serializers.ValidationError(
                {'non_field_errors': ["Email not confirmed."]})

        data['user'] = user_obj
        return data
