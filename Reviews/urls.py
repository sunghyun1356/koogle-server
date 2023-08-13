from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()


urlpatterns =[
    path('', include(router.urls)),
    path('<str:restaurant_name>/review_detail/<str:order_by>/', ReviewListInfoAPIView.as_view()),
    path('<str:restaurant_name>/review_detail/country/<str:country_name>/', ReviewListInfoCountryAPIView.as_view()),
    path('<str:restaurant_name>/create_review/', ReviewCreateListAPIView.as_view()),
]