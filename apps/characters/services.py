from django.contrib.auth import get_user_model
from django.http import QueryDict

from characters.models import (
    CharactersAPIKey,
    Character,
)
from characters.serializers import (
    CharacterSerializer,
    CharacterIDSerializer,
)
from utils.constants import ACCESS_LEVELS
from utils.logger import get_logger
from utils.response_patterns import generate_response


logger = get_logger(__name__)
User = get_user_model()


def get_key(user: User) -> (int, dict):
    logger.info(
        msg=f'Получение API ключа персонажей для пользователя {user}',
    )

    try:
        api_key, _ = CharactersAPIKey.objects.get_or_create(
            access_level=user.level
        )
    except Exception as exc:
        logger.error(
            msg=f'Не удалось получить API ключ персонажей для пользователя {user} '
                f'Ошибки: {exc}',
        )
        return generate_response(
            status_code=500,
        )

    response_data = {
        'api_key': api_key.key,
    }
    logger.info(
        msg=f'Получен API ключ персонажей для пользователя {user}',
    )
    return generate_response(
        status_code=200,
        data=response_data,
    )


def get_level(api_key: str) -> (int, str):
    logger.info(
        msg=f'Получение уровня по API ключу персонажей {api_key}',
    )
    if not api_key:
        logger.info(
            msg=f'API ключ персонажей {api_key} не предоставлен',
        )
        return 200, ACCESS_LEVELS[0][0]

    try:
        key = CharactersAPIKey.objects.filter(
            key=api_key,
        ).first()
    except Exception as exc:
        logger.error(
            msg=f'Не удалось проверить API ключ персонажей {api_key} '
                f'Ошибки: {exc}',
        )
        return 500, '0'

    if key is None:
        logger.info(
            msg=f'API ключ персонажей {api_key} не найден',
        )
        return 404, '0'

    level = key.access_level
    logger.info(
        msg=f'Уровень {level} по API ключу персонажей {api_key} получен',
    )
    return 200, level


def get_characters_by_level(api_key: str) -> (int, dict):
    logger.info(
        msg=f'Получение списка персонажей по ключу {api_key}',
    )

    status_code, level = get_level(
        api_key=api_key,
    )
    if status_code != 200:
        return generate_response(
            status_code=status_code,
        )

    try:
        levels = CharactersAPIKey.objects.filter(
            on=False,
        ).values_list('access_level', flat=True)
        characters = Character.objects.filter(
            level__lte=level,
            is_available=True,
        ).exclude(
            level__in=list(levels),
        )
    except Exception as exc:
        logger.error(
            msg=f'Не удалось получить список персонажей уровня {level} '
                f'Ошибки: {exc}',
        )
        return generate_response(
            status_code=500,
        )

    response_data = CharacterSerializer(
        instance=characters,
        many=True,
    ).data
    logger.info(
        msg=f'Список персонажей по API ключу персонажей {api_key} получен',
    )
    return generate_response(
        status_code=200,
        data=response_data,
    )


def get_characters_by_ids(api_key: str, data: QueryDict) -> (int, dict):
    ids = data.get('characters_ids')
    logger.info(
        msg=f'Получение списка персонажей по ключу {api_key} '
            f'и списку id {ids}',
    )

    serializer = CharacterIDSerializer(
        data=data,
    )
    if not serializer.is_valid():
        logger.error(
            msg=f'Невалидные данные для получения списка персонажей '
                f'по ключу {api_key} и списку id {ids} '
                f'Ошибки: {serializer.errors}',
        )
        return generate_response(
            status_code=400,
        )

    status_code, level = get_level(
        api_key=api_key,
    )
    if status_code != 200:
        return generate_response(
            status_code=status_code,
        )

    try:
        levels = CharactersAPIKey.objects.filter(
            on=False,
        ).values_list('access_level', flat=True)
        characters = Character.objects.filter(
            level__lte=level,
            id__in=ids,
            is_available=True,
        ).exclude(
            level__in=list(levels),
        )
    except Exception as exc:
        logger.error(
            msg=f'Не удалось получить список персонажей уровня {level} '
                f'по списку id {ids}'
                f'Ошибки: {exc}',
        )
        return generate_response(
            status_code=500,
        )

    response_data = CharacterSerializer(
        instance=characters,
        many=True,
    ).data
    logger.info(
        msg=f'Список персонажей по API ключу персонажей {api_key} '
            f'и списку id {ids} получен',
    )
    return generate_response(
        status_code=200,
        data=response_data,
    )
