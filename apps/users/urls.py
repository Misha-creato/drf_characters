from django.urls import path


from users.api import (
    RegisterView,
    AuthView,
    RefreshTokenView,
    LogoutView,
    CustomUserView,
    ConfirmEmailView,
    PasswordRestoreRequestView,
    PasswordRestoreView,
)


urlpatterns = [
    path(
        'register/',
        RegisterView.as_view(),
    ),
    path(
        'auth/',
        AuthView.as_view(),
    ),
    path(
        'auth/refresh/',
        RefreshTokenView.as_view(),
    ),
    path(
        'logout/',
        LogoutView.as_view(),
    ),
    path(
        'confirm_email/',
        ConfirmEmailView.as_view(),
    ),
    path(
        'password_restore/request/',
        PasswordRestoreRequestView.as_view(),
    ),
    path(
        'password_restore/',
        PasswordRestoreView.as_view(),
    ),
    path(
        '',
        CustomUserView.as_view(),
    ),
]
