import datetime
from django.conf import settings
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from users.models import User
from users.validators import username_me_denied
from reviews.models import Review, Comment, Genre, Category, Title


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
        read_only=True, slug_field='username')

    class Meta:
        fields = '__all__'
        read_only_fields = ('title',)
        model = Comment


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        model = Genre
        fields = '__all__'


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = '__all__'


class TitleSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(many=True,)
    category = CategorySerializer()
    rating = serializers.DecimalField(max_digits=2, decimal_places=1)

    class Meta:
        fields = ('__all__')
        model = Title


class TitlePostSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        slug_field='username',
        queryset=Category.objects.all(),
    )
    genre = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Genre.objects.all(),
        many=True
    )

    class Meta:
        fields = '__all__'
        model = Title

    def validate_year(self, value):
        year = datetime.today().year
        if year < value:
            raise serializers.ValidationError('Неверный год выпуска')
        return value


class SignUpSerializer(serializers.Serializer):
    username = serializers.RegexField(
        max_length=settings.LIMIT_USERNAME,
        regex=r'^[\w.@+-]+\Z',
        required=True)
    email = serializers.EmailField(max_length=settings.LIMIT_EMAIL,
                                   required=True)

    def validate_username(self, value):
        return username_me_denied(value)


class TokenSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    confirmation_code = serializers.CharField(required=True)


class UserSerializer(serializers.ModelSerializer):
    username = serializers.RegexField(
        max_length=settings.LIMIT_USERNAME,
        regex=r'^[\w.@+-]+\Z',
        validators=[UniqueValidator(
            queryset=User.objects.all(),
            message='Пользователь с таким username уже существует'
        )],
        required=True
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name',
                  'last_name', 'bio', 'role')
        read_only_fields = ('role',)

    def validate_username(self, value):
        return username_me_denied(value)

    def validate_role(self, value):
        if value not in ['admin', 'user', 'moderator']:
            raise serializers.ValidationError(f"Несуществующая роль: {value}")
        return value


class AdminUserSerializer(UserSerializer):
    role = serializers.CharField(read_only=False, required=False)

