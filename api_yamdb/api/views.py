from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db import IntegrityError
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from reviews.models import Category, Comment, Genre, Review, Title
from users.models import User

from .filters import GenreFilter
from .permissions import (IsAdmin, IsAdminOrReadOnly,
                          IsAuthorOrModeRatOrOrAdminOrReadOnly)
from .serializers import (AdminUserSerializer, CategorySerializer,
                          CommentSerializer, GenreSerializer, ReviewSerializer,
                          SignUpSerializer, TitlePostSerializer,
                          TitleSerializer, TokenSerializer, UserSerializer)


class CustomViewSet(mixins.CreateModelMixin, mixins.ListModelMixin,
                    mixins.DestroyModelMixin, viewsets.GenericViewSet):
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class ReviewViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthorOrModeRatOrOrAdminOrReadOnly,)
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, pk=title_id)
        serializer.save(author=self.request.user, title=title)

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, pk=title_id)
        return title.reviews.all()


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = (IsAuthorOrModeRatOrOrAdminOrReadOnly,)

    def perform_create(self, serializer):
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(Review, pk=review_id)
        serializer.save(author=self.request.user, review=review)

    def get_queryset(self):
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(Review, pk=review_id)
        return review.comments.all()


class SignUpApiView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data.get('username')
        email = serializer.validated_data.get('email')
        try:
            user, _ = User.objects.get_or_create(
                username=username, email=email
            )
        except IntegrityError:
            return Response('Этот username или email уже используется',
                            status.HTTP_400_BAD_REQUEST)
        confirmation_code = default_token_generator.make_token(user)
        send_mail(
            'Код подтверждения',
            f'Код подтверждения: {confirmation_code}',
            settings.DEFAULT_FROM_EMAIL,
            [serializer.validated_data.get('email')]
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class TokenApiView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data.get('username')
        confirmation_code = serializer.validated_data.get('confirmation_code')
        user = get_object_or_404(User, username=username)
        if not default_token_generator.check_token(user, confirmation_code):
            message = (
                'Невалидный код подтверждения.')
            return Response({message}, status=status.HTTP_400_BAD_REQUEST)
        token = RefreshToken.for_user(user)
        return Response({'token': str(token.access_token)},
                        status=status.HTTP_200_OK)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = AdminUserSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']
    permission_classes = (IsAdmin,)
    filter_backends = (filters.SearchFilter,)
    lookup_field = 'username'
    search_fields = ('=username',)

    @action(
        methods=['patch', 'get'],
        detail=False,
        permission_classes=(IsAuthenticated,),
    )
    def me(self, request):
        user = get_object_or_404(User, username=self.request.user)
        serializer = UserSerializer(user)
        if request.method == 'PATCH':
            if user.is_admin:
                serializer = AdminUserSerializer(user, data=request.data,
                                                 partial=True)
            else:
                serializer = UserSerializer(user, data=request.data,
                                            partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class GenreViewSet(CustomViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class CategoryViewSet(CustomViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend, )
    filterset_class = GenreFilter
    search_fields = ('category', 'genre', 'name', 'year')

    def get_serializer_class(self):
        if self.request.method in ['POST', 'PATCH', 'DELETE']:
            return TitlePostSerializer
        return TitleSerializer

    def get_queryset(self):
        if self.action in ['list', 'retrieve']:
            return Title.objects.annotate(rating=Avg('reviews__score'))
        return Title.objects.all()
