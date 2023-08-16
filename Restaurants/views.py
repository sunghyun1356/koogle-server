from django.shortcuts import render
import datetime
import geopy.distance
from collections import Counter

from django.db.models import Count,F
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.core.paginator import Paginator
from geopy.distance import great_circle
from django.contrib.gis.measure import Distance


from rest_framework import generics
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.exceptions import NotFound
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import api_view


from .models import *
from Reviews.models import *
# Create your views here.
from .serializers import *

# 이름, 전화번호, 주소, 오픈, 클로즈 시간, 예약 유무, 가게 사진 필요
# 현재 내위치가 가게로 부터 몇미터 떨어져 있는지 -> 계산 필요
# 몇 쿠글로 예상이 되는지 -> 계산 필요 ( 유저와 네이버를 통해서 각각 )
# 

@api_view(['GET'])
def get_restaurants_by_selected_items(request, food_id):
    selected_items = request.data.get('selected_items', [])
    sort_by = request.data.get('sort_by')

    if not selected_items:
        return Response({"error": "No selected items provided"}, status=400)

    user_latitude = request.data.get('latitude')  # 사용자 위치의 위도
    user_longitude = request.data.get('longitude')  # 사용자 위치의 경도

    restaurants = Restaurant.objects.filter(
        restaurant_food__food__id__in=selected_items
    ).distinct()

    # 거리순 정렬
    if sort_by == 'distance':
        restaurants = sorted(
            restaurants,
            key=lambda restaurant: distance(
                (user_latitude, user_longitude),
                (restaurant.latitude, restaurant.longitude)
            ).m
        )

        # 거리를 계산하여 응답 데이터에 추가
        serialized_data = []
        for restaurant in restaurants:
            distance = great_circle(
                (restaurant.latitude, restaurant.longitude),
                (user_latitude, user_longitude)
            ).meters
            serialized_data.append({
                "restaurant_info": RestaurantBaseSerializer(restaurant).data,
                "distance": distance  # 거리 정보를 추가
            })

    #평점순 정렬
    elif sort_by == 'rating':
        restaurants = restaurants.order_by('-koogle_ranking')
        serialized_data = RestaurantBaseSerializer(restaurants, many=True).data



def main_page(request):
    categories = Category.objects.all()
    return render(request, 'main_page.html', {'categories': categories})


#검색창
@api_view(['GET'])
def search_restaurants(request):
    search_query = request.GET.get('q')  # 검색
    
    if search_query:
        matching_restaurants = Restaurant.objects.filter(name__icontains=search_query)
        serialized_data = RestaurantBaseSerializer(matching_restaurants, many=True).data
        return Response(serialized_data)
    else:
        return Response([])
    


def restaurant_detail(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, pk=restaurant_id)
    restaurant.visit_count += 1
    restaurant.save()
    
    return render(request, 'restaurant_detail.html', {'restaurant': restaurant})



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
            naver_users = User.objects.filter(is_staff=True)
        except User.DoesNotExist:
            raise NotFound("User not found")
        try:
            user_users = User.objects.filter(is_staff=False)
        except User.DoesNotExist:
            raise NotFound("User not found")
        # 오픈시간 클로즈시간 가져오기
        open_close_data ={}
        open_close = OpenHours.objects.all()
        for open_hours in open_close:
            restaurant_name = open_hours.restaurant.name
            day =open_hours.day
            open_time = open_hours.open_time.strftime('%H:%M %p')
            close_time = open_hours.close_time.strftime('%H:%M %p')

            open_close_data[day] ={
                'open_time' : open_time,
                'close_time' : close_time,
            }

        # for문으로 돌리면서 리스트에 담아주고 또 이걸 분류를 해주어야 한다
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
        
        restaurant_menu = Menu.objects.filter(restaurant=restaurant_base)
        # __in은 foreign키로 연결되어있을때 역참조를 위한 것
        menu_detail = Menu_Detail.objects.filter(menu__in=restaurant_menu)
        paginator = Paginator(menu_detail,6)
        page_num =1
        page_obj = paginator.get_page(page_num)
        menus=[]
        for detail in menu_detail:
            menus.append({
                'name' : detail.name,
                'price': detail.price,
                'image': detail.image,
            })

        
        # 이미지 추가 예정
        #restuarant에서 모든 food를 타고 올라가서 category를 출력 해준다
        base_food = Restaurant_Food.objects.filter(restaurant=restaurant_base)
        for food_relation in base_food:
            categories = food_relation.food.category.name


        naver_review_count_sum = 0
        user_review_count_sum = 0
        naver_review_likes_count_sum =0
        user_review_likes_count_sum =0

        for naver_user in naver_users:

            # naver리뷰수 
            naver_review_count_sum += Review.objects.filter(user=naver_user, restaurant = restaurant_base).count()
            # 레스토랑의 라이크수 합
            naver_review_likes_count_sum  += Review_Likes.objects.filter(review__restaurant=restaurant_base, review__user=naver_user).count()
         
        naver_reviews = Review.objects.filter(user__is_staff=True, restaurant=restaurant_base)
        naver_top_likes = Review_Likes.objects.filter(review__in=naver_reviews).values('likes__likes').annotate(like_count=Count('likes')).order_by('-like_count')[:5]
        
        naver_likes_data ={}
        for likes_info in naver_top_likes:
            likes_name = likes_info['likes__likes']
            likes_count = likes_info['like_count']
            naver_likes_data[likes_name] = likes_count

        for user_user in user_users:
            # user리뷰수 
            user_review_count_sum += Review.objects.filter(user=user_user, restaurant = restaurant_base).count()
            # user의 라이크수 합
            user_review_likes_count_sum  += Review_Likes.objects.filter(review__restaurant=restaurant_base, review__user=user_user).count()

        user_reviews = Review.objects.filter(user__is_staff=False, restaurant=restaurant_base)
        user_top_likes = Review_Likes.objects.filter(review__in=user_reviews).values('likes__likes').annotate(like_count=Count('likes')).order_by('-like_count')[:5]
        user_likes_data ={}
        for likes_info in user_top_likes:
            likes_name = likes_info['likes__likes']
            likes_count = likes_info['like_count']
            user_likes_data[likes_name] = likes_count
        
        data = {
            #이미지 파일 넣으면 postman에서 오류떠서 나중에 넣을게욤
            'name' : restaurant_base.name,
            'phone' : restaurant_base.phone,
            'address' : restaurant_base.address,
            'opening_closing_time' : open_close_data,
            'reservation' : restaurant_base.reservation,
            'naver_koogle' : koogle_cal(naver_review_likes_count_sum , naver_review_count_sum),
            'user_koogle' : koogle_cal(user_review_likes_count_sum, user_review_count_sum),
            'category':categories,
            'distance' : distance,
            'naver_likes_data' : naver_likes_data,
            'user_likes_data' : user_likes_data,
            'restaurant_map_url' : restaurant_base.map_link,
            'restaurant_menu' : menus,
            'restaurant_image': restaurant_base.image,
            
        }
        return Response(data)

