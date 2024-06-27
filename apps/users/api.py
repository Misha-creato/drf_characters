from rest_framework.response import Response
from rest_framework.views import APIView

from users.services import register


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
