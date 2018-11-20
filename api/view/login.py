from rest_framework.views import  APIView
from api.models import UserToken,User
from api.utils.response import BaseResponse
from rest_framework.response import Response

class LoginView(APIView):
    def post(self,request):
        response =BaseResponse()
        try:
            print(request.data)
            user = request.data.get("user")
            pwd = request.data.get("pwd")

            user = User.objects.filter(user=user, pwd=pwd).first()
            import uuid
            random_str = uuid.uuid4()
            if user:

                UserToken.objects.update_or_create(user=user, defaults={"token": random_str})
                response.user = user.user
                response.token = random_str
            else:
                response.code = 1001
                response.error = "用户名或者密码错误"

        except Exception as e:
            response.code = 1002
            response.error = str(e)

        return Response(response.dict)