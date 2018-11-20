from rest_framework.viewsets import ModelViewSet
from api.models import *

from api.utils.serializer import CourseDetailSerializers

class CourseDetailView(ModelViewSet):
    queryset = CourseDetail.objects.all()
    serializer_class = CourseDetailSerializers