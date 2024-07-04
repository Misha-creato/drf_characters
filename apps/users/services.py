import uuid
from typing import Callable

from django.contrib.auth import authenticate
from django.db import IntegrityError
from django.http import QueryDict
from django.urls import reverse

from rest_framework_simplejwt.tokens import RefreshToken

from notifications.services import Email

from users.models import CustomUser
from users.serializers import (
    RegisterSerializer,
    ChangedPasswordSerializer,
    AuthSerializer,
    DetailAndUpdateSerializer,
    PasswordRestoreRequestSerializer,
    PasswordRestoreSerializer,
    RefreshAndLogoutSerializer,
)

from utils.logger import (
    get_logger,
    get_log_user_data,
)
from utils.response_patterns import generate_response
from utils.constants import (
    CONFIRM_EMAIL,
    PASSWORD_RESTORE,
)


logger = get_logger(__name__)


def register(data: QueryDict, get_url_func: Callable) -> (int, dict):
    user_data = get_log_user_data(
        user_data=dict(data),
    )
    logger.info(
        msg=f'Создание пользователя с данными: {user_data}',
    )

    serializer = RegisterSerializer(
        data=data,
    )
    if not serializer.is_valid():
        logger.error(
            msg=f'Невалидные данные для создание пользователя: {user_data} '
                f'Ошибки валидации: {serializer.errors}',
        )
        return generate_response(
            status_code=400,
        )

    validated_data = serializer.validated_data
    try:
        user = CustomUser.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
        )
    except IntegrityError as exc:
        logger.error(
            msg=f'Пользователь с такими данными уже существует: {user_data} '
                f'Ошибки: {exc}',
        )
        return generate_response(
            status_code=406,
        )
    except Exception as exc:
        logger.error(
            msg=f'Не удалось создать пользователя с данными: {user_data} '
                f'Ошибки: {exc}',
        )
        return generate_response(
            status_code=500,
        )

    logger.info(
        msg=f'Успешно создан пользователь с данными: {user_data}',
    )
    send_email_by_type(
        user=user,
        get_url_func=get_url_func,
        email_type=CONFIRM_EMAIL,
    )

    try:
        token = RefreshToken.for_user(
            user=user,
        )
    except Exception as exc:
        logger.error(
            msg=f'Не удалось получить токен для аутентификации пользователя с данными: {user_data} '
                f'Ошибки: {exc}',
        )
        return generate_response(
            status_code=201,
        )

    refresh = str(token)
    access = str(token.access_token)
    response_data = {
        'refresh': refresh,
        'access': access
    }
    return generate_response(
        status_code=200,
        data=response_data,
    )


def auth(data: QueryDict) -> (int, dict):
    user_data = get_log_user_data(
        user_data=dict(data),
    )
    logger.info(
        msg=f'Аутентификация пользователя с данными: {user_data}',
    )

    serializer = AuthSerializer(
        data=data,
    )
    if not serializer.is_valid():
        logger.error(
            msg=f'Невалидные данные для аутентификации пользователя с данными: {user_data} '
                f'Ошибки валидации: {serializer.errors}',
        )
        return generate_response(
            status_code=400,
        )

    try:
        user = authenticate(
            email=data['email'],
            password=data['password'],
        )
    except Exception as exc:
        logger.error(
            msg=f'Не удалось аутентифицировать пользователя с данными: {user_data} '
                f'Ошибки: {exc}',
        )
        return generate_response(
            status_code=500,
        )

    if user is None:
        logger.error(
            msg=f'Не удалось аутентифицировать пользователя с данными: {user_data} '
                f'Ошибки: Неправильныe email или пароль',
        )
        return generate_response(
            status_code=401,
        )

    try:
        token = RefreshToken.for_user(
            user=user,
        )
    except Exception as exc:
        logger.error(
            msg=f'Не удалось получить токен при аутентификации пользователя с данными: {user_data} '
                f'Ошибки: {exc}',
        )
        return generate_response(
            status_code=500,
        )

    refresh = str(token)
    access = str(token.access_token)
    response_data = {
        'refresh': refresh,
        'access': access
    }
    logger.info(
        msg=f'Успешная аутентификация пользователя с данными: {user_data}',
    )
    return generate_response(
        status_code=200,
        data=response_data,
    )


def refresh_token(data: QueryDict) -> (int, dict):
    logger.info(
        msg=f'Обновление токена',
    )

    serializer = RefreshAndLogoutSerializer(
        data=data,
    )
    if not serializer.is_valid():
        logger.error(
            msg=f'Невалидные данные для обновления токена '
                f'Ошибки валидации: {serializer.errors}',
        )
        return generate_response(
            status_code=400,
        )

    validated_data = serializer.validated_data
    try:
        refresh = RefreshToken(validated_data['refresh'])
    except Exception as exc:
        logger.error(
            msg=f'Не удалось обновить токен '
                f'Ошибки: {exc}',
        )
        return generate_response(
            status_code=403,
        )

    response_data = {
        'access': str(refresh.access_token),
    }
    try:
        refresh.blacklist()
    except Exception as exc:
        logger.error(
            msg=f'Не удалось удалить токен '
                f'Ошибки: {exc}',
        )
        return generate_response(
            status_code=500,
        )

    refresh.set_jti()
    refresh.set_exp()
    refresh.set_iat()
    response_data['refresh'] = str(refresh)
    logger.info(
        msg=f'Успешно обновлен токен'
    )
    return generate_response(
        status_code=200,
        data=response_data,
    )


def logout(data: QueryDict, user: CustomUser) -> (int, dict):
    logger.info(
        msg=f'Выход из системы пользователя {user}',
    )

    serializer = RefreshAndLogoutSerializer(
        data=data,
    )
    if not serializer.is_valid():
        logger.error(
            msg=f'Невалидные данные для выхода из системы пользователя {user} '
                f'Ошибки валидации: {serializer.errors}',
        )
        return generate_response(
            status_code=400,
        )

    validated_data = serializer.validated_data
    try:
        refresh = RefreshToken(validated_data['refresh'])
    except Exception as exc:
        logger.error(
            msg=f'Невалидный токен для выхода пользователя {user} '
                f'Ошибки: {exc}',
        )
        return generate_response(
            status_code=500,
        )

    try:
        refresh.blacklist()
    except Exception as exc:
        logger.error(
            msg=f'Не удалось удалить токен пользователя {user} '
                f'Ошибки: {exc}',
        )
        return generate_response(
            status_code=500,
        )

    logger.info(
        msg=f'Успешный выход из системы пользователя {user} ',
    )
    return generate_response(
        status_code=200,
    )


def confirm_email(url_hash: str) -> (int, dict):
    logger.info(
        msg=f'Подтверждение email пользователя с хэшем: {url_hash}',
    )

    try:
        user = CustomUser.objects.filter(
            url_hash=url_hash,
        ).first()
    except Exception as exc:
        logger.error(
            msg=f'Подтверждение email. Ошибка при поиске пользователя с хэшем {url_hash} '
                f'Ошибки: {exc}',
        )
        return generate_response(
            status_code=500,
        )

    if user is None:
        logger.error(
            msg=f'При подтверждении email не найден пользователь с хэшем: {url_hash}',
        )
        return generate_response(
            status_code=404,
        )

    user.email_confirmed = True
    user.url_hash = None
    try:
        user.save()
    except Exception as exc:
        logger.error(
            msg=f'Не удалось подтвердить email пользователя {user} с хэшем: {url_hash} '
                f'Ошибки: {exc}',
        )
        return generate_response(
            status_code=500,
        )

    logger.info(
        msg=f'Успешно подтвержден email пользователя {user}',
    )
    return generate_response(
        status_code=200,
    )


def change_password(data: QueryDict, user: CustomUser) -> (int, dict):
    logger.info(
        msg=f'Смена пароля пользователя {user}',
    )

    serializer = ChangedPasswordSerializer(
        instance=user,
        data=data,
    )
    if not serializer.is_valid():
        logger.error(
            msg=f'Невалидные данные для смены пароля пользователя {user} '
                f'Ошибки: {serializer.errors}',
        )
        return generate_response(
            status_code=400,
        )

    validated_data = serializer.validated_data
    user.set_password(validated_data['new_password'])
    try:
        user.save()
    except Exception as exc:
        logger.error(
            msg=f'Не удалось сменить пароль пользователя {user}'
                f'Ошибки: {exc}',
        )
        return generate_response(
            status_code=500,
        )

    logger.info(
        msg=f'Успешно изменен пароль пользователя {user}',
    )
    return generate_response(
        status_code=200,
    )


def detail(user: CustomUser) -> (int, dict):
    logger.info(
        msg=f'Получение данных пользователя {user}',
    )

    response_data = DetailAndUpdateSerializer(
        instance=user,
    ).data

    logger.info(
        msg=f'Данные пользователя {user} успешно получены: {response_data}',
    )
    return generate_response(
        status_code=200,
        data=response_data,
    )


def update(data: QueryDict, user: CustomUser) -> (int, dict):
    user_data = get_log_user_data(
        user_data=dict(data),
    )
    logger.info(
        msg=f'Обновление данных пользователя {user}: {user_data}',
    )

    serializer = DetailAndUpdateSerializer(
        instance=user,
        data=data,
    )
    if not serializer.is_valid():
        logger.error(
            msg=f'Невалидные данные для обновления пользователя {user} '
                f'Ошибки: {serializer.errors}',
        )
        return generate_response(
            status_code=400,
        )

    try:
        serializer.update(
            instance=user,
            validated_data=serializer.validated_data,
        )
    except Exception as exc:
        logger.error(
            msg=f'Не удалось обновить данные пользователя {user}: {user_data} '
                f'Ошибки: {exc}',
        )
        return generate_response(
            status_code=500,
        )

    logger.info(
        msg=f'Успешное обновление данных пользователя {user}: {user_data}',
    )
    return generate_response(
        status_code=200,
        data=serializer.data,
    )


def remove(user: CustomUser) -> (int, dict):
    email = user.email
    logger.info(
        msg=f'Удаление пользователя {email}',
    )

    try:
        user.delete()
    except Exception as exc:
        logger.error(
            msg=f'Не удалось удалить пользователя {email} '
                f'Ошибки: {exc}',
        )
        return generate_response(
            status_code=500,
        )

    logger.info(
        msg=f'Успешное удаление пользователя {email}',
    )
    return generate_response(
        status_code=200,
    )


def password_restore_request(data: QueryDict, get_url_func: Callable) -> (int, dict):
    user_data = get_log_user_data(
        user_data=dict(data),
    )
    logger.info(
        msg=f'Запрос на восстановление пароля пользователя: {user_data}',
    )

    serializer = PasswordRestoreRequestSerializer(
        data=data,
    )
    if not serializer.is_valid():
        logger.error(
            msg=f'Невалидные данные для запроса на восстановление пароля пользователя: {user_data} '
                f'Ошибки: {serializer.errors}',
        )
        return generate_response(
            status_code=400,
        )

    try:
        user = CustomUser.objects.filter(
            email=data['email'],
        ).first()
    except Exception as exc:
        logger.error(
            msg=f'Запрос на восстановление пароля. Ошибка при поиске пользователя с данными {user_data} '
                f'Ошибки: {exc}',
        )
        return generate_response(
            status_code=500,
        )

    if user is None:
        logger.error(
            msg=f'При запросе на восстановление пароля не найден пользователь с {user_data} '
        )
        return generate_response(
            status_code=406,
        )

    status_code = send_email_by_type(
        user=user,
        email_type=PASSWORD_RESTORE,
        get_url_func=get_url_func,
    )

    if status_code != 200:
        logger.error(
            msg=f'Запрос на восстановление пароля пользователя {user_data} не прошел',
        )
    else:
        logger.info(
            msg=f'Запрос на сброс пароля пользователя {user_data} прошел успешно',
        )
    return generate_response(
        status_code=status_code,
    )


def password_restore(url_hash: str, data: QueryDict) -> (int, dict):
    logger.info(
        msg=f'Восстановление пароля пользователя с хэшем: {url_hash}',
    )

    try:
        user = CustomUser.objects.filter(
            url_hash=url_hash,
        ).first()
    except Exception as exc:
        logger.error(
            msg=f'Восстановление пароля. Ошибка при поиске пользователя с хэшем {url_hash} '
                f'Ошибки: {exc}',
        )
        return generate_response(
            status_code=500,
        )

    if user is None:
        logger.error(
            msg=f'При восстановлении пароля не найден пользователь с хэшем: {url_hash}',
        )
        return generate_response(
            status_code=404,
        )

    serializer = PasswordRestoreSerializer(
        instance=user,
        data=data,
    )
    if not serializer.is_valid():
        logger.error(
            msg=f'Невалидные данные для восстановления пароля пользователя: {user} '
                f'Ошибки: {serializer.errors}',
        )
        return generate_response(
            status_code=400,
        )

    validated_data = serializer.validated_data
    user.set_password(validated_data['new_password'])
    user.url_hash = None
    try:
        user.save()
    except Exception as exc:
        logger.error(
            msg=f'Не удалось восстановить пароль пользователя {user}'
                f'Ошибки: {exc}',
        )
        return generate_response(
            status_code=500,
        )

    logger.info(
        msg=f'Успешно восстановлен пароль пользователя {user}',
    )
    return generate_response(
        status_code=200,
    )


def send_email_by_type(user: CustomUser, get_url_func: Callable, email_type: str) -> int:
    '''
    Отправка письма по типу

    Args:
        user: пользователь
        get_url_func: функция для создания ссылки
        email_type: тип письма

    Returns:
        Статус
    '''

    logger.info(
        msg=f'Получение данных для формирования текста '
            f'письма {email_type} пользователю {user}',
    )

    url_hash = str(uuid.uuid4())
    user.url_hash = url_hash

    try:
        user.save()
    except Exception as exc:
        logger.error(
            msg=f'Не удалось получить данные для формирования текста письма {email_type} '
                f'пользователю {user}'
                f'Ошибки: {exc}',
        )
        return 500

    url = get_url_func(reverse(email_type, args=(user.url_hash,)))
    mail_data = {
        'url': url,
    }

    logger.info(
        msg=f'Данные для формирования текста письма {email_type} '
            f'пользователю {user} получены: {mail_data}',
    )

    email = Email(
        email_type=email_type,
        mail_data=mail_data,
        recipient=user,
    )
    status = email.send()
    return status
