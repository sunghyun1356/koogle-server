from rest_framework import serializers

from .models import *
from Users.models import User

#기본적 네이버 리뷰 보여주기 
class ReviewNaverBaseSerializer(serializers.ModelSerializer):
    pass
#기본적 유저 리뷰 보여주기 + 작성하기
class ReviewUserBaseSerializer(serializers.ModelSerializer):
    pass