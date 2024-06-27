from django.db import IntegrityError
from django.http import QueryDict

from users.models import CustomUser
from users.serializers import (
    RegisterSerializer,
    ChangedPasswordSerializer,
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
    # send_email
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
            msg=f'При подтверждении email возникла ошибка в поиске '
                f'пользователя с хэшем: {url_hash} Ошибки: {exc}',
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
