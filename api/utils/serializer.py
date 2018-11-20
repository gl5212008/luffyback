from rest_framework import serializers
from api.models import Course, CourseDetail

class CourseSerializers(serializers.ModelSerializer):

    # course_detail_id = serializers.CharField(source='coursedetail.pk')
    course_detail_id = serializers.CharField(source="coursedetail.pk")
    print(course_detail_id)
    level = serializers.SerializerMethodField()
    def get_level(self,obj):
        return  obj.get_level_display()

    course_name = serializers.SerializerMethodField()
    def get_course_name(self,obj):
        return obj.get_course_name_display()

    price = serializers.SerializerMethodField()
    def get_price(self,obj):
        print(obj.price_policy.all())

        return obj.price_policy.all().first().price

    price_policy_list = serializers.SerializerMethodField()
    def get_price_policy_list(self,obj):
        tem=[]
        for policy_obj in obj.price_policy.all():
            tem.append({
                "price_policy_id":policy_obj.pk,
                'price':policy_obj.price,
                'valid_period':policy_obj.get_valid_period_display()
            })
        return tem


    class Meta:
        model = Course
        fields = '__all__'


class CourseDetailSerializers(serializers.ModelSerializer):

    pricepolicy = serializers.CharField(source='course.price_policy')
    course_name = serializers.CharField(source='course.name')
    recommend_courses = serializers.SerializerMethodField()
    def get_recommend_courses(self,obj):
        # print(obj)
        tem = []
        for course in obj.recommend_courses.all():
            tem.append(
                {
                    'pk':course.pk,
                    'name':course.name,
                    'course_detail_pk':course.coursedetail.pk
                }
            )
        return tem

    class Meta:
        model = CourseDetail
        fields = '__all__'


