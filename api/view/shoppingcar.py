from rest_framework.views import APIView
from rest_framework.viewsets import ViewSetMixin
from api.utils.auth_class import UserAuth
from django.http import HttpResponse
from api.utils.response import BaseResponse
from api.models import Course
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.response import Response
from api.utils.exception import PriceDoseNotExist
from django_redis import get_redis_connection
from django.conf import settings
import json
redis = get_redis_connection("default")
class ShoppingCarView(ViewSetMixin,APIView):
    authentication_classes = [UserAuth]


    def list(self,request, *args, **kwargs):
        response = BaseResponse()

        try:
            shopping_car_key = settings.SHOPPING_CAR_KEY%(request.user.pk,'*')
            shopping_car_list = redis.keys(shopping_car_key)
            # print('hahahah',shopping_car_list)
            shopping_car_course_list = []
            for key in shopping_car_list:
                tem={
                    # "id": redis.hget(key, 'id'),
                    "name":redis.hget(key,'name').decode('utf-8'),
                    'course_img':redis.hget(key,'course_img').decode('utf-8'),
                    'price_policy_dict':json.loads(redis.hget(key,'price_policy_dict').decode('utf-8')),
                    "default_price_policy_id":redis.hget(key,"default_price_policy_id").decode('utf-8')
                }
                shopping_car_course_list.append(tem)
            response.data = shopping_car_course_list
        except Exception as e:
            response.code = 1005
            response.error = '数据调取失败'
        print(response.dict)
        return Response(response.dict)

    def create(self,request, *args, **kwargs):
        response = BaseResponse()
        try:
            user_id = request.user.pk  # auth_class中传过来的 token.user, token.token
            course_id = request.data.get("course_id")
            price_policy_id = request.data.get("price_policy_id")

            course_obj = Course.objects.get(pk=course_id)  #第一次可能报错

            price_policy_list = course_obj.price_policy.all()
            price_policy_dict = {}
            for price_policy_obj in price_policy_list:
                price_policy_dict[price_policy_obj.pk] = {
                        'price':price_policy_obj.price,
                        "valid_period":price_policy_obj.valid_period,
                        "valid_period_text":price_policy_obj.get_valid_period_display(),

                }
            print(price_policy_id)
            print(price_policy_dict)
            if price_policy_id not in price_policy_dict:  #第二次可能报错
                raise PriceDoseNotExist

            # redis = get_redis_connection("default")
            shopping_car_key = settings.SHOPPING_CAR_KEY%(user_id, course_id)
            course_info = {
                'name':course_obj.name,
                "course_img":course_obj.course_img,
                "price_policy_dict":json.dumps(price_policy_dict),
                "default_price_policy_id":price_policy_id
            }
            # print(shopping_car_key)
            # print(course_info)
            redis.hmset(shopping_car_key, course_info)
            print(redis.hgetall('shopping_car_1_1'))
            # for key,val in redis.hgetall("shopping_car_1_1").items():
            #     print(key.decode('utf-8'),':',val.decode('utf-8'))
            response.msg = "成功加入购物车"


        except ObjectDoesNotExist as e:
            response.code = 1002
            response.error = "没有该课程"

        except PriceDoseNotExist as e:
            response.code = 1003
            response.error = e.error
        except Exception as e:
            response.code = 1004
            response.error = str(e)
        return Response(response.dict)

    def destroy(self,request,*args,**kwargs):
        response = BaseResponse()
        try:
            course_id = request.query_params.get('course_id')
            key = settings.SHOPPING_CAR_KEY%(request.user.pk,course_id)
            redis = get_redis_connection()
            redis.delete(key)
            response.msg = "删除成功"
        except Exception as e:
            response.data = 1006
            response.error = "删除不成功"
        return Response(response.dict)

    def update(self,request,*args,**kwargs):
        response = BaseResponse()
        try:
            course_id = request.data.get('course_id')
            policy_id = str(request.data.get("price_policy_id")) if request.data.get("price_policy_id") else None
            # print(policy_id)
            # policy_id = 2

            key = settings.SHOPPING_CAR_KEY%(request.user.pk,course_id)
            # print(key)
            if not redis.exists(key):
                response.code = 1007
                response.error = "课程不存在"
                return Response(response.dict)

            price_policy_dict = json.loads(redis.hget(key,'price_policy_dict').decode('utf-8'))
            # print(price_policy_dict)
            if policy_id not in price_policy_dict:
                response.code = 1008
                response.error = "价格周期不存在"
                return Response(response.dict)

            redis.hset(key,"default_price_policy_id",policy_id)
            response.data = "修改成功"
            return Response(response.dict)
        except Exception as e:
            response.code = 1009
            response.error = str(e)
            print(e)
            return Response(response.dict)