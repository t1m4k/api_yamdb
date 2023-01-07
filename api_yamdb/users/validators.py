from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core import exceptions


class UsernameRegexValidator(UnicodeUsernameValidator):
    regex = r'^[\w.@+-]+\Z'
    flags = 0


def username_me_denied(value):
    if value == 'me':
        raise exceptions.ValidationError(
            'Имя пользователя "me" запрещено!'
        )
    return value
