
from rest_framework.viewsets import ModelViewSet
from api.models import *

from api.utils.serializer import CourseSerializers

class CourseView(ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializers