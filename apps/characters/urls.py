from django.urls import path

from characters.api import (
    APIKeyView,
    CharacterListView,
)


urlpatterns = [
    path(
        'get_key/',
        APIKeyView.as_view(),
    ),
    path(
        '',
        CharacterListView.as_view(),
    ),
]
