from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from .serializers import SetNewPasswordSerializer
from .functions import send_password_reset_email


class PasswordResetRequestView(APIView):
    """
    API view to initiate a password reset request.

    Accepts an email address and sends a password reset link to the user if the account exists
    and is active.

    Methods:
        post(request): Handles the password reset email request.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        """
        Handles the POST request to send a password reset email.

        Args:
            request (Request): The HTTP request containing the user's email.

        Returns:
            Response: A message indicating that the reset email has been sent.
        """
        email = request.data.get("email")
        send_password_reset_email(email, request)
        return Response({"detail": "Folge dem Link in der Email zum Zurücksetzen des Passwortes."}, status=status.HTTP_200_OK)


class PasswordResetConfirmView(APIView):
    """
    API view to confirm and complete the password reset process.

    Accepts a password reset token and new password information, verifies the token, and
    updates the user's password.

    Methods:
        post(request): Validates and sets the new password.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        """
        Handles the POST request to reset the user's password.

        Args:
            request (Request): The HTTP request containing UID, token, and new passwords.

        Returns:
            Response: A message confirming the password reset or validation errors.
        """
        serializer = SetNewPasswordSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"detail": "Passwort wurde erfolgreich geändert."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
