from django.contrib.auth import authenticate
from django.db import IntegrityError
from django.http import QueryDict
from rest_framework_simplejwt.tokens import RefreshToken

from users.models import CustomUser
from users.serializers import (
    RegisterSerializer,
    ChangedPasswordSerializer,
    AuthSerializer,
    DetailAndUpdateSerializer,
    PasswordRestoreRequestSerializer,
    PasswordRestoreSerializer,
)

from utils.logger import (
    get_logger,
    get_log_user_data,
)
from utils.response_patterns import generate_response


logger = get_logger(__name__)


def register(data: QueryDict) -> (int, dict):
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
    # TODO send_email
    return generate_response(
        status_code=200,
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
            msg=f'Не удалось получить токен при аутентификации пользователя с данными: {user_data}',
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


def password_restore_request(data: QueryDict) -> (int, dict):
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
        )
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

    # TODO send mail


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
