from typing import Any
from django.db import models
from Users.models import *
from Restaurants.models import *
# Create your models here.

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name="review_restaurant")
    content = models.TextField(max_length= 1000, verbose_name="content", null=False)
    image_1 = models.ImageField(upload_to="",null=True)
    image_2 = models.ImageField(upload_to="",null=True)
    image_3 = models.ImageField(upload_to="", null=True)
    created_at = models.DateTimeField(auto_created=True)
    koogle = models.IntegerField(verbose_name="koogle")
    
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