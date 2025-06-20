from rest_framework import serializers
from rest_framework.authtoken.models import Token


class TokenSerializer(serializers.Serializer):
    """
    Serializer to validate an authentication token with a corresponding user ID.

    Fields:
        token (str): The authentication token key, write-only.
        ID (int): The user ID expected to be associated with the token, write-only.
    """

    token = serializers.CharField(write_only=True)
    ID = serializers.IntegerField(write_only=True)

    def validate(self, data):
        """
        Validate that the provided token exists and belongs to the user with the given ID.

        Args:
            data (dict): Input data containing 'token' and 'ID'.

        Returns:
            dict: The validated data with an added 'user' key referencing the token's user.

        Raises:
            serializers.ValidationError: If the token does not exist or does not belong to the user ID.
        """
        token_key = data.get('token')
        user_id = data.get('ID')

        try:
            token_obj = Token.objects.get(key=token_key)
        except Token.DoesNotExist:
            raise serializers.ValidationError("Token does not exist")

        if token_obj.user.id != user_id:
            raise serializers.ValidationError(
                "Token does not belong to this user ID")

        data['user'] = token_obj.user
        return data
