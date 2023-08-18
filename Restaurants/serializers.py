from rest_framework import serializers

from Users.models import User
from .models import *

# 이름, 쿠글, 카테고리, 음식, 전화번호, 주소, 오픈, 클로즈 시간, 예약 유무, 가게 사진 필요
class RestaurantBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        fields = '__all__'


class CategoryFoodSerializer(serializers.ModelSerializer):
    class Meta:
        model = Food
        fields = '__all__'

class FoodSelectedRestaurantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        fields = '__all__'
