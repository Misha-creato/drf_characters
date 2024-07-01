from django.contrib import admin

from characters.models import (
    Character,
    CharactersAPIKey,
)


@admin.register(Character)
class CharacterAdmin(admin.ModelAdmin):
    pass


@admin.register(CharactersAPIKey)
class CharactersAPIKeyAdmin(admin.ModelAdmin):
    list_display = [
        'key',
        'access_level',
    ]
