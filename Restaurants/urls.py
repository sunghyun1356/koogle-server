from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()


urlpatterns =[
    path('', include(router.urls)),
    path('<str:restaurant_name>/', RestaurantsBaseAPIView.as_view()),
]