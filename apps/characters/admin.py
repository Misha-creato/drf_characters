from django.contrib import admin

from characters.models import (
    Character,
    CharactersAPIKey,
)


@admin.register(Character)
class CharacterAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'level',
        'is_available',
    ]
    list_editable = [
        'is_available',
    ]
    list_display_links = [
        'level',
    ]
    list_filter = [
        'level',
    ]

    actions = ['make_available', 'make_unavailable']

    def make_available(self, request, queryset):
        queryset.update(is_available=True)
    make_available.short_description = 'Сделать доступными'

    def make_unavailable(self, request, queryset):
        queryset.update(is_available=False)
    make_unavailable.short_description = 'Сделать недоступными'



@admin.register(CharactersAPIKey)
class CharactersAPIKeyAdmin(admin.ModelAdmin):
    list_display = [
        'key',
        'access_level',
    ]
