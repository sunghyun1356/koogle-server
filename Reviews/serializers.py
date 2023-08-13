from rest_framework import serializers

from .models import *
from Users.models import User

#기본적 리뷰 보여주기 
class ReviewNaverBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields ='__all__'
#리뷰작성하기 + 작성하기
class ReviewUserBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields ='__all__'

class ReviewCreateListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['content', 'star']
        