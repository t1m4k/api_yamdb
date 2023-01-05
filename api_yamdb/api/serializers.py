from django.conf import settings
from django.core.exceptions import ValidationError
from rest_framework import serializers

from reviews.models import Review, Comment
from users.models import User
from users.validators import username_me_denied


class TitleSerializer(serializers.ModelSerializer):
    rating = serializers.DecimalField(max_digits=2, decimal_places=1)


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )

    def create(self, validated_data):
        if Review.objects.filter(
                author=self.context['request'].user,
                title=self.validated_data.get('title')).exists:
            raise serializers.ValidationError(
                'Возможно оставить только один обзор'
            )
        return Review.objects.create(**validated_data)

    class Meta:
        fields = '__all__'
        read_only_fields = ('title',)
        model = Review


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )

    class Meta:
        fields = '__all__'
        read_only_fields = ('title',)
        model = Comment


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
        return value


class TokenSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    confirmation_code = serializers.CharField(required=True)


class UserSerializer(serializers.ModelSerializer):
    username = serializers.RegexField(max_length=settings.LIMIT_USERNAME,
                                      regex=r'^[\w.@+-]+\Z', required=True)

    class Meta:
        abstract = True
        model = User
        fields = ('username', 'email', 'first_name',
                  'last_name', 'bio', 'role')

    def validate_username(self, value):
        if (
                self.context.get('request').method == 'POST'
                and User.objects.filter(username=value).exists()
        ):
            raise ValidationError(
                'Пользователь с таким именем уже существует.'
            )
        return username_me_denied(value)


class UserWriteSerializer(UserSerializer):
    role = serializers.CharField(read_only=True)
