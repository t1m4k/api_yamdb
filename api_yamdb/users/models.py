from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models

from users.validators import UsernameRegexValidator, username_me_denied


class User(AbstractUser):
    USER = 'user'
    ADMIN = 'admin'
    MODERATOR = 'moderator'

    ROLE_CHOICES = [
        (USER, USER),
        (ADMIN, ADMIN),
        (MODERATOR, MODERATOR),
    ]

    username_validator = UsernameRegexValidator()
    username = models.CharField(
        max_length=settings.LIMIT_USERNAME,
        unique=True,
        validators=[username_validator, username_me_denied],
        error_messages={
            'unique': "Пользователь с таким username уже существует",
        },
    )
    email = models.EmailField(
        max_length=settings.LIMIT_EMAIL,
        unique=True,
        error_messages={
            'unique': "Пользователь с таким email уже существует",
        },
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=USER)
    first_name = models.CharField(max_length=settings.LIMIT_USERNAME,
                                  blank=True)
    bio = models.TextField(blank=True)

    @property
    def is_user(self):
        return self.role == self.USER

    @property
    def is_moderator(self):
        return self.role == self.MODERATOR

    @property
    def is_admin(self):
        return self.role == self.ADMIN or self.is_superuser or self.is_staff

    class Meta:
        ordering = ('id',)

    def __str__(self):
        return self.username
