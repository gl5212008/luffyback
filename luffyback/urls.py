"""luffyback URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url,include
from django.contrib import admin
from rest_framework import routers
from api.view.course import CourseView
from api.view.coursedetail import CourseDetailView
from api.view.login import LoginView
from api.view.shoppingcar import ShoppingCarView
from api.view.account import AccountView

router = routers.DefaultRouter()
router.register("course",CourseView)
router.register("coursedetail",CourseDetailView)

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^', include(router.urls)),
    url(r'^login/$', LoginView.as_view()),
    url(r'^shopping_car/$', ShoppingCarView.as_view({'get':'list','post':'create','put':'update','delete':'destroy'})),
    # url(r'^shopping_car/(?P<pk>\d+)/$', ShoppingCarView.as_view({'put':'update','delete':'destroy'})),

    url(r'^account/$', AccountView.as_view({'get':'list','post':'create'})),
]
