from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

from .serializers import RegisterSerializer
from .functions import send_activation_email

User = get_user_model()


class RegisterView(APIView):
    """
    API view to handle user registration.

    Permissions:
        AllowAny: Accessible without authentication.

    POST:
        Accepts registration data, validates and creates a new user.
        Sends an activation email after successful registration.
        Returns a success message or an error message on failure.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            send_activation_email(user, request)
            return Response(
                {"message": "Please confirm your email address."},
                status=status.HTTP_201_CREATED
            )
        return Response(
            "Bitte überprüfe deine Eingaben und versuche es erneut.",
            status=status.HTTP_400_BAD_REQUEST
        )


class ActivateAccountView(APIView):
    """
    API view to activate a user account via emailed link.

    Permissions:
        AllowAny: Accessible without authentication.

    GET:
        Accepts a base64 encoded user ID and token as URL parameters.
        Validates the token and activates the user account if valid.
        Returns appropriate success or error messages.
    """
    permission_classes = [AllowAny]

    def get(self, request, uidb64, token):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            if user.is_active:
                return Response(
                    {"message": "Bitte überprüfe deine Eingaben und versuche es erneut."},
                    status=status.HTTP_200_OK
                )
            user.is_active = True
            user.save()
            return Response(
                {"message": "Account activated successfully!"},
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"message": "Invalid or expired activation link."},
                status=status.HTTP_400_BAD_REQUEST
            )
