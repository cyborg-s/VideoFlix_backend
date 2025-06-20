from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token

from .serializers import LoginSerializer


class LoginView(APIView):
    """
    API view for handling user login.
    Accepts POST requests with email and password, validates the credentials,
    and returns an authentication token upon success.
    """
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        """
        Handles POST request for user login.

        Args:
            request (Request): The incoming HTTP request containing login data.

        Returns:
            Response: A successful response with token and user information,
                      or an error response with validation errors.
        """
        serializer = LoginSerializer(data=request.data)
        print(serializer)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'email': user.email,
                'user_id': user.id
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
