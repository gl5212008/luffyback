from rest_framework.authentication import BaseAuthentication
from api.models import UserToken, User
from rest_framework.exceptions import AuthenticationFailed
from api.utils.response import BaseResponse

class UserAuth(BaseAuthentication):

    def authenticate(self, request):
        token = request.query_params.get('token')

        token = UserToken.objects.filter(token=token).first()
        if token:
            return token.user, token.token

        else:
            response = BaseResponse()
            response.code = 1001
            response.error = '认证失败'
            raise AuthenticationFailed(response.dict)