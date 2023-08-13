from django.shortcuts import render
import datetime
import geopy.distance
from collections import Counter

from django.db.models import Count, Avg
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
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
from rest_framework.generics import CreateAPIView

from .models import *
from Restaurants.models import *
from .serializers import *

# Create your views here.


# review 디테일 페이지 기본 -> 최신순으로 배정

# country별로 뽑아올 때
class ReviewListInfoCountryAPIView(generics.ListAPIView):
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
        return f"{days} dyas, {hours}hours, {minutes}minutes ago"

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

        country_reviews = Review.objects.filter(user__in=country_users, restaurant=restaurant_base)
        country_review_paginator = Paginator(country_reviews, 10)
        country_review_page = request.query_params.get('country_review_page',1)
        country_reviews_data = self.get_review_data(country_review_paginator.get_page(country_review_page), restaurant_base)

        restaurants_info = {
            'restaurant_name': restaurant_base.name,
                'address': restaurant_base.address,
                'total_review': Review_Restaurant.objects.filter(restaurant=restaurant_base).count(),
                'avg_star' : Review.objects.filter(restaurant=restaurant_base).aggregate(Avg('star'))['star__avg'],}
        data = {
            'restaurants_info' : restaurants_info,
            'country_reviews': country_reviews_data,
            'country_list' : all_countries,

        }
        
        return Response(data)

    def get_review_data(self, reviews, restaurant_base):
        
        review_data = []
        for review in reviews:
            user_reviews = Review.objects.filter(user=review.user)
            total_review_count = user_reviews.count()
            total_image_count = sum(1 for r in user_reviews if r.image_1 or r.image_2 or r.image_3)

            data = {
                
                'username': review.user.username,
                'star': review.star,
                'total_review_count': total_review_count,
                'total_image_count': total_image_count,
                'content': review.content,
                'country': review.user.country.name if review.user.country else None,
                'created_at' :  self.calculate_time(review),
            }
            review_data.append(data)
        
        return review_data

              
            

class ReviewListInfoAPIView(generics.ListAPIView):
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
        return f"{days} dyas, {hours}hours, {minutes}minutes ago"

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
                'total_review': Review_Restaurant.objects.filter(restaurant=restaurant_base).count(),
                'avg_star' : Review.objects.filter(restaurant=restaurant_base).aggregate(Avg('star'))['star__avg'],}
        data = {
            'restaurants_info' : restaurants_info,
            'naver_reviews': naver_reviews_data,
            'user_reviews': user_reviews_data,
            'country_list'  : all_countries,

        }
        
        return Response(data)

    def get_review_data(self, reviews, restaurant_base):
        review_data = []
        for review in reviews:
            user_reviews = Review.objects.filter(user=review.user)
            total_review_count = user_reviews.count()
            total_image_count = sum(1 for r in user_reviews if r.image_1 or r.image_2 or r.image_3)
            
            data = {
                
                'username': review.user.username,
                'star': review.star,
                'created_at' :  self.calculate_time(review),
                'total_review_count': total_review_count,
                'total_image_count': total_image_count,
                'content': review.content,
                'country': review.user.country.name if review.user.country else None,
            }
            review_data.append(data)
        
        return review_data
    
# user정하고, 레스토랑 정하고, 내용넣고, 이미지 넣고, created_at은 자동설정, koogle설정 란은 없고, star는 지정해준다
# likes들 란이 있으면 그중에서 5개를 선택해서 지정한다. -> review_likes에 저장이 된다.q
class ReviewCreateListAPIView(generics.GenericAPIView):
    queryset = Review.objects.all()
    # serializer시키기
    serializer_class = ReviewCreateListSerializer
    permission_classes = [AllowAny]

    def post(self, request,restaurant_name, *args, **kwargs):
        try:
            restaurant_base = Restaurant.objects.get(name=restaurant_name)
        except Restaurant.DoesNotExist:
            raise NotFound("Restaurant not found")
        all_reviews = Review.objects.filter(restaurant=restaurant_base)
        all_likes_list =[]
        for review in all_reviews:
            likes_list = review.review_review_likes.values_list('likes__likes', flat=True)
            all_likes_list.extend(likes_list)
        all_likes_list = list(set(all_likes_list))

        user = review.user
        content = request.data.get('content')
        star = request.data.get('star')

        all_likes_list = request.data.get('all_likes_list', [])

        review_data ={
            'user' : user,
            'restaurant' : restaurant_base,
            'content' : content,
            'star' : star,
            'created_at' : timezone.now(),
        }
        review = Review.objects.create(**review_data)
        for index, like_value in enumerate(all_likes_list):
            if like_value ==1:
                like_name = Likes.objects.get(pk=index + 1).likes
                like = Likes.objects.get(likes=like_name)
                Review_Likes.objects.create(review=review, likes=like)
        
        serializer = self.get_serializer(data=review_data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
       
        return Response(serializer.data, status=status.HTTP_201_CREATED)


        
