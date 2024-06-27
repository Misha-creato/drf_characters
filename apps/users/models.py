import io
from PIL import Image

from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager,
)

from utils.constants import ACCESS_LEVELS


AVATAR_SIZE_WIDTH = 100
AVATAR_SIZE_HEIGHT = 100


class CustomUserManager(BaseUserManager):
    def create_user(self, email: str, password: str, **extra_fields):
        if not email:
            raise ValueError('Требуется электронная почта')
        email = self.normalize_email(email=email)
        user = self.model(email=email, **extra_fields)
        user.set_password(raw_password=password)
        user.save()
        return user

    def create_superuser(self, email: str, password: str):
        return self.create_user(
            email=email,
            password=password,
            is_superuser=True,
            is_staff=True,
        )


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(
        verbose_name='Адрес электронной почты',
        unique=True,
    )
    avatar = models.ImageField(
        default='avatars/default.jpeg',
        verbose_name='Аватар',
        upload_to='avatars',
    )
    thumbnail = models.ImageField(
        default='thumbnails/default.jpeg',
        verbose_name='Миниатюра',
        upload_to='thumbnails',
    )
    is_superuser = models.BooleanField(
        verbose_name='Статус суперпользователя',
        default=False
    )
    is_staff = models.BooleanField(
        verbose_name='Статус персонала',
        default=False,
    )
    is_active = models.BooleanField(
        verbose_name='Статус активности',
        default=True,
    )
    email_confirmed = models.BooleanField(
        verbose_name='Адрес электронной почты подтвержден',
        default=False,
    )
    url_hash = models.CharField(
        verbose_name='Хэш',
        max_length=128,
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
    date_joined = models.DateTimeField(
        verbose_name='Дата регистрации',
        auto_now_add=True,
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __make_thumbnail(self) -> None:

        with Image.open(self.avatar) as img:
            if img.mode in ('RGBA', 'LA'):
                img = img.convert('RGB')

            img.thumbnail((AVATAR_SIZE_WIDTH, AVATAR_SIZE_HEIGHT))
            thumb = io.BytesIO()
            img.save(thumb, format='JPEG', quality=90)

            self.thumbnail = SimpleUploadedFile(self.avatar.name, thumb.getvalue())

    def save(self, *args, **kwargs):
        if self.avatar and self.pk:
            old_avatar = CustomUser.objects.get(pk=self.pk).avatar
            if self.avatar != old_avatar:
                self.__make_thumbnail()
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'users'
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
