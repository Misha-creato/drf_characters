from django.urls import path

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from users.api import (
    RegisterView,
)


urlpatterns = [
    path(
        'register/',
        RegisterView.as_view(),
    ),
    path(
        'token/',
        TokenObtainPairView.as_view(),
    ),
    path(
        'token/refresh/',
        TokenRefreshView.as_view(),
    ),
]