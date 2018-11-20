from rest_framework.views import APIView
from rest_framework.viewsets import ViewSetMixin
from api.utils.auth_class import UserAuth
from django.http import HttpResponse
from api.utils.response import BaseResponse
from api.models import Course, Coupon, CouponRecord
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.response import Response
from api.utils.exception import PriceDoseNotExist
from django_redis import get_redis_connection
from django.conf import settings
import json
import datetime


class AccountView(ViewSetMixin, APIView):
    authentication_classes = [UserAuth]
    redis = get_redis_connection("default")

    def create(self, request, *args, **kwargs):
        response = BaseResponse()

        course_id_list = request.data.get("course_id_list")
        print(course_id_list)

        # 清除
        keys = self.redis.keys("account_%s_*"%(request.user.pk))
        if keys:
            self.redis.delete(*keys)

        account_course = {}
        try:
            for course_id in course_id_list:
                account_key = settings.ACCOUNT_KEY%(request.user.pk, course_id)

                course_obj = Course.objects.get(pk=course_id)

                course_detail_list = self.redis.hgetall("shopping_car_%s_%s"%(request.user.pk,course_id))
                # print(course_detail_list)
                course_detail = {}
                for key,val in course_detail_list.items():
                    if key.decode('utf-8') == 'price_policy_dict':
                        course_detail[key.decode('utf8')] = json.loads(val.decode('utf8'))
                    else:
                        course_detail[key.decode('utf8')] = val.decode('utf8')
                # print(course_detail)
                account_course["course_detail"] = course_detail

                # coupon_record_list
                time_now = datetime.datetime.now()
                coupon_record_list = CouponRecord.objects.filter(
                                                                user=request.user,
                                                                status=0,
                                                                coupon__valid_begin_date__lt=time_now,
                                                                coupon__valid_end_date__gt=time_now,
                                                                )

                coupon_course = {}
                coupon_global = {}
                for coupon_record_obj in coupon_record_list:
                    coupon_info = {
                                    "name":coupon_record_obj.coupon.name,
                                    "coupon_type":coupon_record_obj.coupon.get_coupon_type_display(),
                                    "money_equivalent_value":coupon_record_obj.coupon.money_equivalent_value,
                                    "off_percent":coupon_record_obj.coupon.off_percent,
                                    "minimum_consume":coupon_record_obj.coupon.minimum_consume,
                                    "object_id":coupon_record_obj.coupon.object_id,
                                    }
                    object_id = coupon_info.get("object_id")
                    if object_id:
                        coupon_course[coupon_record_obj.pk] = coupon_info
                    else:
                        coupon_global[coupon_record_obj.pk] = coupon_info

                account_course["course_coupon"] = json.dumps(coupon_course)
                # print(account_course)
                # print("|"*50)
                # print(coupon_global)
                # print("========================================================")
                self.redis.hmset(account_key,account_course)
                self.redis.hmset("coupon_global_%s"%request.user.pk, coupon_global)
            response.msg = "结算成功"
            return Response(response.dict)

        except ObjectDoesNotExist as e:
            response.code = 1002
            response.error = "课程不存在"
            return Response(response.dict)


            '''
            account_userid_courseid:{

                    course_detail:{}

                    course_coupon:{}

            }
            global_coupon_userid:{}


            '''

    def list(self,request, *args, **kwargs):
        response = BaseResponse()
        response.data = {}

        # account_info
        account_info_key_list = self.redis.keys("account_%s_*"%(request.user.pk))
        for account_info_key in account_info_key_list:
            account_info = self.redis.hgetall(account_info_key)

            for key,val in account_info.items():
                if key.decode('utf8') == 'course_coupon':
                    response.data[account_info_key.decode('utf-8')] = {key.decode('utf8'): json.loads(val.decode('utf8'))}
                else:
                    response.data[account_info_key.decode('utf-8')] = {key.decode('utf8'):val.decode('utf8')}

        # global_coupon
        global_coupon = self.redis.hgetall("coupon_global_%s" % request.user.pk)
        new_global_coupon = {}
        for key, val in global_coupon.items():
            new_global_coupon[key.decode('utf8')] = val.decode('utf-8')
        response.data["global_coupon"] = new_global_coupon
        return Response(response.dict)





