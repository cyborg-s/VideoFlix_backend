from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.auth import get_user_model

User = get_user_model()


class SetNewPasswordSerializer(serializers.Serializer):
    """
    Serializer for setting a new password using a token-based reset mechanism.

    This serializer validates the password reset token and UID from the reset
    link, verifies that the two password fields match, and sets the new password
    for the user.

    Fields:
        uid (str): Base64-encoded user ID from the reset link.
        token (str): Password reset token for verification.
        new_password (str): The new password to be set.
        new_password_confirm (str): Confirmation of the new password.
    """

    uid = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True)
    new_password_confirm = serializers.CharField(write_only=True)

    def validate(self, data):
        """
        Validates that the new passwords match, the UID is valid, and the token is correct.

        Raises:
            serializers.ValidationError: If passwords do not match, the UID is invalid,
                                         or the token is invalid or expired.

        Returns:
            dict: Validated data with the user instance added.
        """
        if data["new_password"] != data["new_password_confirm"]:
            raise serializers.ValidationError(
                "Passwörter stimmen nicht überein.")

        try:
            uid = urlsafe_base64_decode(data["uid"]).decode()
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise serializers.ValidationError("Ungültiger Link.")

        token_generator = PasswordResetTokenGenerator()
        if not token_generator.check_token(user, data["token"]):
            raise serializers.ValidationError(
                "Ungültiger oder abgelaufener Token.")

        data["user"] = user
        return data

    def save(self):
        """
        Saves the new password for the validated user.

        Returns:
            User: The updated user instance with the new password.
        """
        user = self.validated_data["user"]
        user.password = make_password(self.validated_data["new_password"])
        user.save()
        return user
