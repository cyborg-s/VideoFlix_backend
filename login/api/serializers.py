from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate

User = get_user_model()

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        try:
            user_obj = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid credentials.")

        if not user_obj.check_password(password):
            raise serializers.ValidationError("Invalid credentials.")

        if not user_obj.is_active:
            raise serializers.ValidationError("Email not confirmed.")

        data['user'] = user_obj
        return data
