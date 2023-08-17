from rest_framework import serializers

from .models import *
from Users.models import User, Country


class ReviewUserBaseSerializer(serializers.ModelSerializer):
    country = serializers.SlugRelatedField(
        queryset = Country.objects.all(),
        slug_field='name'
    )
    class Meta:
        model = Review
        fields = '__all__'

    def create(self, validated_data):
        all_likes_data = self.context['request'].data.get('all_likes_data', [])
        
        # Review 객체 생성
        review = Review.objects.create(**validated_data)

        for like_id in all_likes_data:
            if int(like_id) == 1:
                try:
                    like = Likes_Restaurant.objects.filter(restaurant=review.restaurant).order_by('pk').first()
                    Review_Likes.objects.create(review=review, likes=like.likes)
                except (ValueError, Likes_Restaurant.DoesNotExist, IndexError):
                    pass

        return review



        