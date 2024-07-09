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
    '''
    Получение API ключа

    Args:
        user: пользователь

    Returns:
        Код статуса и словарь данных
        200,
        {
            "message": "Успех",
            "data": {
                "api_key": "123"
            }
        }
    '''

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
    '''
    Получение уровня

    Args:
        api_key: API ключ

    Returns:
        Код статуса и уровень
        200, '0'
    '''

    logger.info(
        msg='Получение уровня по API ключу персонажей',
    )

    if not api_key:
        logger.info(
            msg='API ключ персонажей не предоставлен',
        )
        return 200, ACCESS_LEVELS[0][0]

    try:
        key = CharactersAPIKey.objects.filter(
            key=api_key,
        ).first()
    except Exception as exc:
        logger.error(
            msg=f'Не удалось найти API ключ персонажей '
                f'Ошибки: {exc}',
        )
        return 500, '0'

    if key is None:
        logger.error(
            msg='API ключ персонажей не найден',
        )
        return 404, '0'

    level = key.access_level
    logger.info(
        msg=f'Уровень {level} по API ключу персонажей получен',
    )
    return 200, level


def get_characters_by_level(api_key: str) -> (int, dict):
    '''
    Получение списка персонажей по уровню

    Args:
        api_key: API ключ

    Returns:
        Код статуса и словарь данных
        200,
        {
            "message": "Успех",
            "data": []
        }
    '''

    logger.info(
        msg='Получение списка персонажей по API ключу персонажей',
    )

    status_code, level = get_level(
        api_key=api_key,
    )
    if status_code != 200:
        logger.error(
            msg='Не удалось получить список персонажей по API ключу персонажей',
        )
        return generate_response(
            status_code=status_code,
        )

    try:
        levels = CharactersAPIKey.objects.filter(
            activated=False,
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
        msg=f'Список персонажей {response_data} по API ключу персонажей получен',
    )
    return generate_response(
        status_code=200,
        data=response_data,
    )


def get_characters_by_ids(api_key: str, data: QueryDict) -> (int, dict):
    '''
     Получение списка персонажей по id

     Args:
         api_key: API ключ
         data: данные персонажей
            {
                "characters_ids": [1, 2, "3"]
            }

     Returns:
         Код статуса и словарь данных
         200,
         {
             "message": "Успех",
             "data": []
         }
     '''

    logger.info(
        msg=f'Получение списка персонажей с данными {data}',
    )

    serializer = CharacterIDSerializer(
        data=data,
    )
    if not serializer.is_valid():
        logger.error(
            msg=f'Невалидные данные для получения списка персонажей '
                f'с данными {data} '
                f'Ошибки: {serializer.errors}',
        )
        return generate_response(
            status_code=400,
        )

    status_code, level = get_level(
        api_key=api_key,
    )
    if status_code != 200:
        logger.error(
            msg=f'Не удалось получить список персонажейс данными {data}',
        )
        return generate_response(
            status_code=status_code,
        )

    ids = serializer.validated_data['characters_ids']

    try:
        levels = CharactersAPIKey.objects.filter(
            activated=False,
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
                f'с данными {data} '
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
        msg=f'Список персонажей {response_data} с данными {data} получен',
    )
    return generate_response(
        status_code=200,
        data=response_data,
    )
