from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
from Restaurants.models import *
# Create your models here.

class Review(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name="review_restaurant")
    content = models.TextField(max_length= 1000, verbose_name="content", null=False)
    image_1 = models.ImageField(upload_to="reviews/review-img",default="reviews/review_default-img",null=True)
    image_2 = models.ImageField(upload_to="reviews/review-img",default="reviews/review_default-img",null=True)
    image_3 = models.ImageField(upload_to="reviews/review-img",default="reviews/review_default-img", null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    koogle = models.IntegerField(verbose_name="koogle", default=0)
    star = models.IntegerField(verbose_name="star", default=0)

    def __str__(self):
        return f'Review of {self.restaurant.name} by {self.user.username}: {self.content[:20]}'

    
    @classmethod
    def update_restaurant_reviews(cls, restaurant_instance, reviews):
        if not reviews: reviews = []
        reviews_shortened = [review["content"][:10]+"..." for review in reviews]
        print(f'update_restaurant_reviews({restaurant_instance}, {reviews_shortened})')

        naver_user, _ = get_user_model().objects.get_or_create(is_staff=True)
        existing = cls.objects.filter(user=naver_user, restaurant=restaurant_instance)
        incoming = reviews
        
        incoming_review_instances = []

        for review in incoming:
            instance, _ = cls.objects.get_or_create(**review, user=naver_user, restaurant=restaurant_instance)
            instance.created_at = review['created_at']
            instance.image_1 = review['image_1']
            instance.image_2 = review['image_2']
            instance.image_3 = review['image_3']
            instance.save()

            incoming_review_instances.append(instance)
        
        for review in existing:
            if review not in incoming_review_instances:
                review.delete()

        return incoming_review_instances

class Likes(models.Model):
    likes = models.CharField(max_length=100, verbose_name="likes_type")
    
    def __str__(self):
        return self.likes
#수정
class Review_Likes(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE,related_name="review_review_likes")
    likes = models.ForeignKey(Likes, on_delete=models.CASCADE,related_name="likes_review_likes")

    def __str__(self):
        restaurant_name = self.review.restaurant.name if self.review.restaurant else "Unknown Restaurant"
        likes_type = self.likes.likes if self.likes else "Unknown Likes Type"

        return f"Review: {restaurant_name}'s {likes_type} by {self.review.user.username}"
    
    @classmethod
    def update_review_likes(cls, review_instance, likes):
        print(f'update_review_likes({review_instance}, {likes})')

        if not likes: likes = []
        
        latest_like_ids = []

        for like in likes:
            like_instance, _ = Likes.objects.get_or_create(likes=like)
            cls.objects.get_or_create(
                review=review_instance, 
                likes=like_instance
            )
            latest_like_ids.append(like_instance.id)
        
        existing = cls.objects.filter(review=review_instance)
        for review_like in existing:
            if review_like.likes_id not in latest_like_ids:
                review_like.delete()


class Likes_Restaurant(models.Model):
    likes = models.ForeignKey(Likes, on_delete=models.CASCADE)
    restaurant = models.ForeignKey('Restaurants.Restaurant', on_delete=models.CASCADE)

    def __str__(self):
        return f'Restaurant {self.restaurant} has a like type "{self.likes}"'

    @classmethod
    def update_restaurant_likes(cls, restaurant_instance, likes):
        print(f'update_restaurant_likes({restaurant_instance}, {likes})')

        if not likes: likes = []

        latest_likes_ids = []
        
        for like in likes:
            like_instance, _ = Likes.objects.get_or_create(likes=like)
            cls.objects.get_or_create(
                restaurant=restaurant_instance, 
                likes=like_instance
            )

            latest_likes_ids.append(like_instance.id)

        existing = cls.objects.filter(restaurant=restaurant_instance)
        for restaurant_like in existing:
            if restaurant_like.likes_id not in latest_likes_ids:
                restaurant_like.delete()