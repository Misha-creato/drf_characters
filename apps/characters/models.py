import uuid

from django.db import models

from utils.constants import ACCESS_LEVELS


class Character(models.Model):
    name = models.CharField(
        verbose_name='Имя',
        max_length=256,
        unique=True,
    )
    hp = models.PositiveIntegerField(
        verbose_name='Здоровье',
    )
    attack = models.PositiveIntegerField(
        verbose_name='Атака',
    )
    speed = models.PositiveIntegerField(
        verbose_name='Скорость',
    )
    image = models.ImageField(
        verbose_name='Изображение',
        upload_to='characters/',
        null=True,
        blank=True,
    )
    level = models.CharField(
        verbose_name='Уровень доступа',
        max_length=64,
        null=True,
        choices=ACCESS_LEVELS,
        default=ACCESS_LEVELS[0][0],
    )
    is_available = models.BooleanField(
        verbose_name='Доступен',
        default=True,
    )
    created_at = models.DateTimeField(
        verbose_name='Дата создания',
        auto_now_add=True,
    )

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'characters'
        verbose_name = 'Персонаж'
        verbose_name_plural = 'Персонажи'


class CharactersAPIKey(models.Model):
    key = models.CharField(
        verbose_name='Ключ',
        max_length=64,
    )
    access_level = models.CharField(
        verbose_name='Уровень доступа',
        max_length=64,
        null=True,
        choices=ACCESS_LEVELS,
        default=ACCESS_LEVELS[0][0],
    )
    created_at = models.DateTimeField(
        verbose_name='Дата создания',
        auto_now_add=True,
    )

    def __str__(self):
        return self.key

    class Meta:
        db_table = 'characters_api_keys'
        verbose_name = 'API ключ персонажей'
        verbose_name_plural = 'API ключи персонажей'

    def _make_key(self):
        return str(uuid.uuid4())

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self._make_key()
        return super().save(*args, **kwargs)
