from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from users.services import (
    register,
    auth,
    detail,
    update,
    remove,
    change_password,
    confirm_email,
    password_restore_request,
    password_restore,
)


class RegisterView(APIView):
    def post(self, request):
        data = request.data
        status_code, response_data = register(
            data=data,
        )
        return Response(
            status=status_code,
            data=response_data
        )


class AuthView(APIView):
    def post(self, request):
        data = request.data
        status_code, response_data = auth(
            data=data,
        )
        return Response(
            status=status_code,
            data=response_data
        )


class CustomUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        status_code, response_data = detail(
            user=user,
        )
        return Response(
            status=status_code,
            data=response_data
        )

    def post(self, request):
        user = request.user
        data = request.data
        status_code, response_data = change_password(
            user=user,
            data=data,
        )
        return Response(
            status=status_code,
            data=response_data
        )

    def patch(self, request):
        user = request.user
        data = request.data
        status_code, response_data = update(
            user=user,
            data=data,
        )
        return Response(
            status=status_code,
            data=response_data
        )

    def delete(self, request):
        user = request.user
        status_code, response_data = remove(
            user=user,
        )
        return Response(
            status=status_code,
            data=response_data
        )


class ConfirmEmailView(APIView):
    def get(self, request, url_hash):
        status_code, response_data = confirm_email(
            url_hash=url_hash,
        )
        return Response(
            status=status_code,
            data=response_data
        )


class PasswordRestoreRequestView(APIView):
    def post(self, request):
        data = request.data
        status_code, response_data = password_restore_request(
            data=data,
        )
        return Response(
            status=status_code,
            data=response_data
        )


class PasswordRestoreView(APIView):
    def post(self, request, url_hash):
        data = request.data
        status_code, response_data = password_restore(
            url_hash=url_hash,
            data=data,
        )
        return Response(
            status=status_code,
            data=response_data
        )
