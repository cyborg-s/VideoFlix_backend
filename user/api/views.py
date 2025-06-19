from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .serializers import TokenSerializer

class TokenView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = TokenSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            return Response({"success": True}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
