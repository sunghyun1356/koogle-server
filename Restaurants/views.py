from django.shortcuts import render
import datetime
import geopy.distance

from django.db.models import Count
from django.shortcuts import get_object_or_404
from django.http import JsonResponse

from rest_framework import generics
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.exceptions import NotFound
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet



from .models import *
from Reviews.models import *
# Create your views here.
from .serializers import *

# 이름, 전화번호, 주소, 오픈, 클로즈 시간, 예약 유무, 가게 사진 필요
# 현재 내위치가 가게로 부터 몇미터 떨어져 있는지 -> 계산 필요
# 몇 쿠글로 예상이 되는지 -> 계산 필요 ( 유저와 네이버를 통해서 각각 )
# 

def koogle_cal(a,b):
    if 0<= (a / b)/5 < 1.5:
        c =1
    elif 1.5 <= (a / b)/5 < 3:
        c =2
    elif 3 <= (a/b)/5:
        c=3
    return c 



class RestaurantsBaseAPIView(APIView):
    queryset = Restaurant.objects.all()
    serializers_class = RestaurantBaseSerializer
    permission_classes = [AllowAny]
    
    def get(self, request, restaurant_name ):
        data = dict()

        try:
            restaurant_base = get_object_or_404(Restaurant, name=restaurant_name)
        except Restaurant.DoesNotExist:
            raise NotFound("Restaurant not found")
        
        try:
            naver_user = User.objects.get(username='NAVER')
        except User.DoesNotExist:
            raise NotFound("User not found")
        
        naver_review_count = Review_Restaurant.objects.filter(review__user=naver_user, restaurant = restaurant_base).count()
        naver_review_likes_count = Review_Likes.objects.filter(review__restaurant=restaurant_base, review__user=naver_user).count()
        user_review_count = Review_Restaurant.objects.filter(restaurant = restaurant_base).exclude(review__user=naver_user).count()
        user_review_likes_count = Review_Likes.objects.filter(review__restaurant=restaurant_base).exclude(review__user=naver_user).count()
        #restuarant에서 모든 food를 타고 올라가서 category를 출력 해준다
        base_food = Restaurant_Food.objects.filter(restaurant=restaurant_base)
        for food_relation in base_food:
            categories = food_relation.food.category.name
        restaurant_latitude = restaurant_base.latitude
        restaurant_longtitude = restaurant_base.longitude
        # 추후 api받아와서 설정 할 것
        current_latitude = 0
        current_longtitude =0
        #계산
        distance = geopy.distance.distance((current_latitude,current_longtitude), (restaurant_latitude,restaurant_longtitude)).m
        data = {
            'name' : restaurant_base.name,
            'phone' : restaurant_base.phone,
            'address' : restaurant_base.address,
            'opening_closing_time' : restaurant_base.open_close_time,
            'reservation' : restaurant_base.reservation,
            'naver_koogle' : koogle_cal(naver_review_count , naver_review_likes_count),
            'user_koogle' : koogle_cal(user_review_count , user_review_likes_count),
            'category':categories,
            'distance' : distance,
        }
        return Response(data)