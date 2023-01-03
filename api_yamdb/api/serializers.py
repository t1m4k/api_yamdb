from django.conf import settings
from django.core.exceptions import ValidationError
from rest_framework import serializers

from users.models import User


class SignUpSerializer(serializers.Serializer):
    username = serializers.RegexField(max_length=settings.LIMIT_USERNAME,
                                      regex=r'^[\w.@+-]+\Z', required=True)
    email = serializers.EmailField(max_length=settings.LIMIT_EMAIL,
                                   required=True)

    def validate_username(self, value):
        if value == 'me':
            raise ValidationError(
                'Имя пользователя "me" не разрешено.'
            )
        if User.objects.filter(username=value).exists():
            raise ValidationError(
                f'Пользователь с таким username: {value} - уже существует.'
            )
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise ValidationError(
                f'Пользователь с таким email: {value} - уже существует.'
            )
        return value


class TokenSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    confirmation_code = serializers.CharField(required=True)

    def validate_username(self, value):
        if not User.objects.filter(username=value).exists():
            raise ValidationError(
                f'Пользователь с таким username: {value} - не существует.'
            )
        return value
