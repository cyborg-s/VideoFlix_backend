from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .serializers import TokenSerializer

class TokenView(APIView):
    """
    API view to validate a token and associated user ID.

    This view accepts POST requests with a token and user ID, validates
    the token belongs to the user, and returns a success response if valid.
    """
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        """
        Handle POST requests to validate token and user ID.

        Args:
            request (Request): The request object containing data with 'token' and 'ID'.

        Returns:
            Response: HTTP 200 with success message if valid,
                      HTTP 400 with errors if validation fails.
        """
        serializer = TokenSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            return Response({"success": True}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
