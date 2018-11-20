
from django.utils.deprecation import MiddlewareMixin

class CoreMiddleWare(MiddlewareMixin):

    def process_response(self,request,response):

        response["Access-Control-Allow-Origin"]="*"

        return response