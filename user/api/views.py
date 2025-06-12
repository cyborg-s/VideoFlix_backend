from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import TokenSerializer
from rest_framework.authtoken.models import Token

class TokenView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = TokenSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            # Optional: token ist schon validiert, daher musst du hier nichts mehr machen
            return Response({"success": True}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
