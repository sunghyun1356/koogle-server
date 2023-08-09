from rest_framework import serializers

from Users.models import User
from .models import *

# 이름, 쿠글, 카테고리, 음식, 전화번호, 주소, 오픈, 클로즈 시간, 예약 유무, 가게 사진 필요
class RestaurantBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        fields = '__all__'

# 레스토랑의 메뉴를 가져온다
class RestaurantMenuSerializer(serializers.ModelSerializer):
    pass

# 좋아요 제일 많이 받은것의 이름과 개수를 보여준다
class RestaurantLikeSerializer(serializers.ModelSerializer):
    pass

# 레스토랑의 위치를 네이버 지도로 연결해준다
class RestaurantMapSerializer(serializers.ModelSerializer):
    pass

