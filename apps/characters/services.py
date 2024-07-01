from django.contrib.auth import get_user_model

from characters.models import CharactersAPIKey, Character
from serializers import CharacterSerializer
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
        'key': api_key.key,
    }
    logger.info(
        msg=f'Получен API ключ персонажей для пользователя {user}',
    )
    return generate_response(
        status_code=200,
        data=response_data,
    )


def get_level(api_key: str) -> (int, tuple):
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
        return 500, ()

    if key is None:
        logger.info(
            msg=f'API ключ персонажей {api_key} не найден',
        )
        return 404, ()

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
        characters = Character.objects.filter(
            level=level,
        )
    except Exception as exc:
        logger.error(
            msg=f'Не удалось получить список персонажей уровня {level}',
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
