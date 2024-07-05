from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from characters.services import (
    get_key,
    get_characters_by_level,
    get_characters_by_ids,
)


class APIKeyView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        status_code, response_data = get_key(
            user=user,
        )
        return Response(
            status=status_code,
            data=response_data
        )


class CharacterListView(APIView):

    def get(self, request):
        api_key = request.headers.get('Api-Key', '')
        status_code, response_data = get_characters_by_level(
            api_key=api_key,
        )
        return Response(
            status=status_code,
            data=response_data
        )

    def post(self, request):
        api_key = request.headers.get('Api-Key', '')
        data = request.data
        status_code, response_data = get_characters_by_ids(
            api_key=api_key,
            data=data,
        )
        return Response(
            status=status_code,
            data=response_data
        )
