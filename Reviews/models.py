from typing import Any
from django.db import models
from Users.models import *
from Restaurants.models import *

from django.utils import timezone
from datetime import timedelta
from django.conf import settings

# Create your models here.

class Review(models.Model):
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name="review_restaurant")
    content = models.TextField(max_length= 1000, verbose_name="content", null=False)
    image_1 = models.ImageField(upload_to="",null=True)
    image_2 = models.ImageField(upload_to="",null=True)
    image_3 = models.ImageField(upload_to="", null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    #koogle 값은 처음에 영이였다가 post하면 추후에 저장이 되도록 한다
    koogle = models.IntegerField(verbose_name="koogle", default=0)
    star = models.IntegerField(verbose_name="star",default=0)
    
    
    def calculate_time(self):
        current = timezone.now()
        gap = current - self.created_at
        days = gap.days
        seconds = gap.seconds
        hours, remain = divmod(seconds, 3600)
        minutes, seconds = divmod(remain, 60)
        return f"{days} days, {hours}hours, {minutes}minutes ago"
    
    def __str__(self):
         return f"Overall review for {self.restaurant.name} written by{self.user.username}"
    

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
    
class Review_Restaurant(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE,related_name="review_review_restaurant")
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name="restaurant_review_restaurant")

    def __str__(self):
            restaurant_name = self.restaurant.name if self.restaurant else "Unknown Restaurant"
            return f"Review: for Restaurant: '{restaurant_name}' by {self.review.user.username}"        