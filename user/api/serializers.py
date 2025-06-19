from rest_framework import serializers
from rest_framework.authtoken.models import Token


class TokenSerializer(serializers.Serializer):
    token = serializers.CharField(write_only=True)
    ID = serializers.IntegerField(write_only=True)

    def validate(self, data):
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
