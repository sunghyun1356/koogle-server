from rest_framework import serializers

from .models import *
from Users.models import User


#리뷰작성하기 + 작성하기
class ReviewUserBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields ='__all__'


        