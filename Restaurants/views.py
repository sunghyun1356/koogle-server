from django.shortcuts import render
import datetime
import geopy.distance
from collections import Counter

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
        # 이미지 없을시 설정
        if restaurant_base.image == None:
            restaurant_base.image = "None"
        # NAVER인 놈들이랑 아닌놈들 중에 Likes별 가장 많이 받은것들 이름 뽑아주고 개수 정렬해서 만들어주기
        # review_likes에서 likes_id별로 정렬하는데 이것의 수가 많은대로 정렬하고, 하나하나씩 몇개있는지 뽑아준다
        naver_review_likes =Review_Likes.objects.filter(review__restaurant=restaurant_base, review__user=naver_user).order_by('-likes__id')
        #Counter사용으로 id별로 개수를 세어준다
        naver_likes_counter = Counter(like.likes.id for like in naver_review_likes)
        #Counter가 tuple형식이니 x[1] -> 개수별로 내림차순으로 만들어준다
        sorted_naver_likes = sorted(naver_likes_counter.items(), key=lambda x: x[1], reverse=True)[:5]  
        naver_likes_data = [{'name': Likes.objects.get(id=like_id).likes, 'count': count} for like_id, count in sorted_naver_likes]
        
        user_review_likes =Review_Likes.objects.filter(review__restaurant=restaurant_base).exclude(review__user=naver_user).order_by('-likes__id')
        user_likes_counter = Counter(like.likes.id for like in user_review_likes)
        sorted_user_likes = sorted(user_likes_counter.items(), key=lambda x: x[1], reverse=True)[:5]  
        user_likes_data = [{'name': Likes.objects.get(id=like_id).likes, 'count': count} for like_id, count in sorted_user_likes]

        restaurant_menu = Menu.objects.filter(restaurant=restaurant_base)
        # __in은 foreign키로 연결되어있을때 역참조를 위한 것
        menu_detail = Menu_Detail.objects.filter(menu__in=restaurant_menu)
        menus=[]
        for detail in menu_detail:
            menus.append({
                'name' : detail.name,
                'price': detail.price,
                'conetent' : detail.content,
            })
        # 이미지 추가 예정
        


        data = {
            #이미지 파일 넣으면 postman에서 오류떠서 나중에 넣을게욤
            'name' : restaurant_base.name,
            'phone' : restaurant_base.phone,
            'address' : restaurant_base.address,
            'opening_closing_time' : restaurant_base.open_close_time,
            'reservation' : restaurant_base.reservation,
            'naver_koogle' : koogle_cal(naver_review_count , naver_review_likes_count),
            'user_koogle' : koogle_cal(user_review_count , user_review_likes_count),
            'category':categories,
            'distance' : distance,
            'naver_likes_data' : naver_likes_data,
            'user_likes_data' : user_likes_data,
            'restaurant_map_url' : restaurant_base.map_link,
            'restaurant_menu' : menus,
            
        }
        return Response(data)

