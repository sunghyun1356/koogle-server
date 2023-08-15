from django.shortcuts import render
import datetime
import geopy.distance

from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import timedelta

from rest_framework import generics
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.exceptions import NotFound
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import ListCreateAPIView

from .models import *
from Restaurants.models import *
from .serializers import *
from Users.models import *

# Create your views here.


# review 디테일 페이지 기본 -> 최신순으로 배정

# country별로 뽑아올 때
class ReviewListInfoCountryAPIView(ListCreateAPIView):
    # 객체저장
    queryset = Review.objects.all()
    # serializer시키기
    serializer_class = ReviewUserBaseSerializer
    permission_classes = [AllowAny]
    

    def calculate_time(self, review):
        current = timezone.now()
        gap = current - review.created_at
        days = gap.days
        seconds = gap.seconds
        hours, remain = divmod(seconds, 3600)
        minutes, seconds = divmod(remain, 60)
        return f"{days} days, {hours}hours, {minutes}minutes ago"

    def get_queryset(self):
        country_name = self.request.query_params.get('country_name')
        return country_name

    def list(self, request, restaurant_name,country_name, *args, **kwargs):
        data = dict()
        # 레스토랑 베이스 만들기
        try:
            restaurant_base = get_object_or_404(Restaurant, name=restaurant_name)
        except Restaurant.DoesNotExist:
            raise NotFound("Restaurant not found")
        # country 뽑아주고 저장하기
        if country_name is None:
            raise NotFound("Country name not exits")
        # Country 객체 만들어주기
        try:
            user_country = Country.objects.filter(name=country_name)
        except Country.DoesNotExist:
            raise NotFound("Country not exits")
        # 유저 만들어주기
        try:
            country_users = User.objects.filter(is_staff=False, country__in = user_country)
        except User.DoesNotExist:
            raise NotFound("User not found")

        all_countries = Country.objects.values_list('name', flat=True) 
        all_reviews = Review.objects.filter(restaurant=restaurant_base)
        all_likes_list =[]
        for review in all_reviews:
            likes_list = review.review_review_likes.values_list('likes__likes', flat=True)
            all_likes_list.extend(likes_list)
        all_likes_list = list(set(all_likes_list))

        country_reviews = Review.objects.filter(user__in=country_users, restaurant=restaurant_base)
        country_review_paginator = Paginator(country_reviews, 10)
        country_review_page = request.query_params.get('country_review_page',1)
        country_reviews_data = self.get_review_data(country_review_paginator.get_page(country_review_page), restaurant_base)

        restaurants_info = {
            'restaurant_name': restaurant_base.name,
                'address': restaurant_base.address,
                'total_review': Review.objects.filter(restaurant=restaurant_base).count(),
                'avg_star' : Review.objects.filter(restaurant=restaurant_base).aggregate(Avg('star'))['star__avg'],}
        data = {
            'restaurants_info' : restaurants_info,
            'country_reviews': country_reviews_data,
            'country_list' : all_countries,
            'all_likes_list': all_likes_list,
        }
        
        return Response(data)

    def get_review_data(self, reviews, restaurant_base):
        
        review_data = []
        for review in reviews:
            user_reviews = Review.objects.filter(user=review.user)
            total_review_count = user_reviews.count()
            total_image_count = sum(1 for r in user_reviews if r.image_1 or r.image_2 or r.image_3)

            data = {
                
                'username': review.user.name,
                'star': review.star,
                'total_review_count': total_review_count,
                'total_image_count': total_image_count,
                'content': review.content,
                'country': review.user.country.name if review.user.country else None,
                'created_at' :  self.calculate_time(review),
                'image_1' : review.image_1,
                'image_2' : review.image_2,
                'image_3' : review.image_3,
            }
            review_data.append(data)
        
        return review_data
    def post(self, request, *args, **kwargs):
        # request.data로 전송된 데이터를 받아옴
        restaurant_name = kwargs["restaurant_name"]
        
        # restaurant_name을 기반으로 레스토랑 객체 가져옴
        restaurant_id = Restaurant.objects.get(name=restaurant_name)

        # user_id는 현재 요청을 보낸 사용자
        user_id = request.user.id
        # request.data.에 user필드를 추가
        """request.data["user"] = user_id"""
        request.data["restaurant"] = restaurant_id.id
        # serializer로 데이터 검증 및 저장
        # ㅎ해당 요청의 데이터로 초기화된 serializer 객체를 가져온다
        serializer = self.get_serializer(data=request.data)
        # 유효한지 검사를 한다
        serializer.is_valid(raise_exception=True)
        # 검증된 데이터를 기반으로 Review 모델 인스턴스를 생성하고 저장한다.
        review = serializer.save()

        # Likes 선택 여부를 확인하고 Review_Likes, Likes_Restaurant에 자동으로 저장
        likes_data = request.data.get('all_likes_list', [])
        i = 0
        for like_id in likes_data:
            # 각각의 likes_Restaurant에서 likes의 pk를 얻는다.
            if int(like_id) == 1:
                try:
                    # Likes_Restaurant의 객체 중 restaurant가 review.restaurant인 것들을 가져옴
                    like = Likes_Restaurant.objects.filter(restaurant=review.restaurant).order_by('pk')[i]
                    i += 1
                    # Review_Likes와 Likes_Restaurant에 저장
                    Review_Likes.objects.create(review=review, likes=like.likes)
                except (ValueError, Likes_Restaurant.DoesNotExist, IndexError):
                    pass
            else:
                i+=1

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
                    

class ReviewListInfoAPIView(ListCreateAPIView):
    # 객체저장
    queryset = Review.objects.all()
    # serializer시키기
    serializer_class = ReviewUserBaseSerializer
    permission_classes = [AllowAny]
    # 정렬하기 위해서 설정해준다

    def calculate_time(self, review):
        current = timezone.now()
        gap = current - review.created_at
        days = gap.days
        seconds = gap.seconds
        hours, remain = divmod(seconds, 3600)
        minutes, seconds = divmod(remain, 60)
        return f"{days} days, {hours}hours, {minutes}minutes ago"

    def get_queryset(self):
        # 초반 기본 설정은 latest고 get(a,b)일때 query_param에 get으로 a,b를 가져온다는 것이다
        order_by = self.request.query_params.get('order_by', 'latest') 
        if order_by == 'latest':
            return self.queryset.order_by('-created_at')
        elif order_by == 'highest':
            return self.queryset.order_by('-star')
        elif order_by == 'lowest':
            return self.queryset.order_by('star')

    def list(self, request, restaurant_name, *args, **kwargs):
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
        all_countries = Country.objects.values_list('name', flat=True) 
        all_reviews = Review.objects.filter(restaurant=restaurant_base)
        all_likes_list =[]
        for review in all_reviews:
            likes_list = review.review_review_likes.values_list('likes__likes', flat=True)
            all_likes_list.extend(likes_list)
        all_likes_list = list(set(all_likes_list))

        naver_reviews = Review.objects.filter(user__in=naver_users, restaurant=restaurant_base)
        user_reviews = Review.objects.filter(user__in=user_users, restaurant=restaurant_base)
        
        # naver_reviews가 여러개니까 이걸 대체 몇개씩 볼건지를 정한다 -> 4개찍 naver_reviews가 저장되어있다
        naver_reviews_paginator = Paginator(naver_reviews, 4)

        user_reviews_paginator = Paginator(user_reviews, 4)

        # 네이버와 user사용자의 리뷰페이지 번호를 가져오는데 파라미터가 url에 없으면 기본값은 1
        naver_reviews_page = request.query_params.get('naver_reviews_page', 1)
        user_reviews_page = request.query_params.get('user_reviews_page', 1)
        
        #self.함수로 지금 선언된 함수를 사용한다
        naver_reviews_data = self.get_review_data(naver_reviews_paginator.get_page(naver_reviews_page), restaurant_base)
        # get_page(?_reviews_page로 지금 어느 페이지에 있는지를 가져온다)
        user_reviews_data = self.get_review_data(user_reviews_paginator.get_page(user_reviews_page), restaurant_base)
        restaurants_info = {
            'restaurant_name': restaurant_base.name,
                'address': restaurant_base.address,
                'total_review': Review.objects.filter(restaurant=restaurant_base).count(),
                'avg_star' : Review.objects.filter(restaurant=restaurant_base).aggregate(Avg('star'))['star__avg'],}
        data = {
            'restaurants_info' : restaurants_info,
            'naver_reviews': naver_reviews_data,
            'user_reviews': user_reviews_data,
            'country_list'  : all_countries,
            'all_likes_list' : all_likes_list,

        }
        
        return Response(data)

    def get_review_data(self, reviews, restaurant_base):
        review_data = []
        for review in reviews:
            user_reviews = Review.objects.filter(user=review.user)
            total_review_count = user_reviews.count()
            total_image_count = sum(1 for r in user_reviews if r.image_1 or r.image_2 or r.image_3)
            
            data = {
                
                'username': review.user.name,
                'star': review.star,
                'created_at' :  self.calculate_time(review),
                'total_review_count': total_review_count,
                'total_image_count': total_image_count,
                'content': review.content,
                'country': review.user.country.name if review.user.country else None,
                'image_1' : review.image_1,
                'image_2' : review.image_2,
                'image_3' : review.image_3,
            }
            review_data.append(data)
        
        return review_data
    def post(self, request, *args, **kwargs):
        # request.data로 전송된 데이터를 받아옴
        restaurant_name = kwargs["restaurant_name"]
        
        # restaurant_name을 기반으로 레스토랑 객체 가져옴
        restaurant_id = Restaurant.objects.get(name=restaurant_name)

        # user_id는 현재 요청을 보낸 사용자
        user_id = request.user.id
        # request.data.에 user필드를 추가
        """request.data["user"] = user_id"""
        request.data["restaurant"] = restaurant_id.id
        # serializer로 데이터 검증 및 저장
        # ㅎ해당 요청의 데이터로 초기화된 serializer 객체를 가져온다
        serializer = self.get_serializer(data=request.data)
        # 유효한지 검사를 한다
        serializer.is_valid(raise_exception=True)
        # 검증된 데이터를 기반으로 Review 모델 인스턴스를 생성하고 저장한다.
        review = serializer.save()

        # Likes 선택 여부를 확인하고 Review_Likes, Likes_Restaurant에 자동으로 저장
        likes_data = request.data.get('all_likes_list', [])
        i = 0
        for like_id in likes_data:
            # 각각의 likes_Restaurant에서 likes의 pk를 얻는다.
            if int(like_id) == 1:
                try:
                    # Likes_Restaurant의 객체 중 restaurant가 review.restaurant인 것들을 가져옴
                    like = Likes_Restaurant.objects.filter(restaurant=review.restaurant).order_by('pk')[i]
                    i += 1
                    # Review_Likes와 Likes_Restaurant에 저장
                    Review_Likes.objects.create(review=review, likes=like.likes)
                except (ValueError, Likes_Restaurant.DoesNotExist, IndexError):
                    pass
            else:
                i+=1

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
                       

        
