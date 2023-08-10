from django.shortcuts import render
import datetime
import geopy.distance
from collections import Counter

from django.db.models import Count, Avg
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.core.paginator import Paginator

from rest_framework import generics
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.exceptions import NotFound
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from .models import *
from Restaurants.models import *
from .serializers import *

# Create your views here.


# review 디테일 페이지 기본 -> 최신순으로 배정

# 이름 위치, 거리 필요
# 총 몇개의 리뷰가 있는지와 대략적으로 몇 쿠글인지

class ReviewBaseAPIView(generics.ListAPIView):
    queryset = Restaurant.objects.all()
    serializers_class = Review
    permission_classes = [AllowAny]

    def get(self, request, restaurant_name):
        try:
            restaurant_base = get_object_or_404(Restaurant, name=restaurant_name)
        except Restaurant.DoesNotExist:
            raise NotFound("Restaurant not found")
        
        try:
            naver_users = User.objects.filter(is_staff=True)
            user_users = User.objects.filter(is_staff=False)
        except User.DoesNotExist:
            raise NotFound("User not found")
        
        naver_reviews = Review.objects.filter(user__in=naver_users, restaurant=restaurant_base)
        user_reviews = Review.objects.filter(user__in=user_users, restaurant=restaurant_base)
        
        naver_reviews_paginator = Paginator(naver_reviews, 3)
        user_reviews_paginator = Paginator(user_reviews, 3)
        
        naver_reviews_page = request.query_params.get('naver_reviews_page', 1)
        user_reviews_page = request.query_params.get('user_reviews_page', 1)
        
        naver_reviews_data = self.get_review_data(naver_reviews_paginator.get_page(naver_reviews_page), restaurant_base)
        user_reviews_data = self.get_review_data(user_reviews_paginator.get_page(user_reviews_page), restaurant_base)
        
        data = {
            'naver_reviews': naver_reviews_data,
            'user_reviews': user_reviews_data
        }
        
        return Response(data)

    def get_review_data(self, reviews, restaurant_base):
        review_data = []
        for review in reviews:
            user_reviews = Review.objects.filter(user=review.user)
            total_review_count = user_reviews.count()
            total_image_count = sum(1 for r in user_reviews if r.image_1 or r.image_2 or r.image_3)

            data = {
                'restaurant_name': restaurant_base.name,
                'address': restaurant_base.address,
                'total_review': Review_Restaurant.objects.filter(restaurant=restaurant_base).count(),
                'avg_star': Review.objects.filter(user=review.user, restaurant=restaurant_base).aggregate(Avg('star'))['star__avg'],
                'username': review.user.username,
                'star': review.star,
                'created_at': review.created_at,
                'total_review_count': total_review_count,
                'total_image_count': total_image_count,
                'content': review.content,
                'country': review.user.country.name if review.user.country else None,
            }
            review_data.append(data)
        
        return review_data

class ReviewListInfoAPIView(generics.ListAPIView):
    # 객체저장
    queryset = Review.objects.all()
    # serializer시키기
    serializer_class = ReviewSerializer
    permission_classes = [AllowAny]
    # 정렬하기 위해서 설정해준다
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
                'created_at': review.created_at,
                'total_review_count': total_review_count,
                'total_image_count': total_image_count,
                'content': review.content,
                'country': review.user.country.name if review.user.country else None,
            }
            review_data.append(data)
        
        return review_data