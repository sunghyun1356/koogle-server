from django.db import models
from enum import unique
from rest_framework.exceptions import ValidationError
# Create your models here.


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="category_name")
    image = models.ImageField(upload_to="", default='media/default_image.jpeg')
    def __str__(self):
        return self.name
    
class Food(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="food_category")
    name = models.CharField(max_length=100, verbose_name="Food_name")
    image = models.ImageField(upload_to="", default='media/default_image.jpeg')
    def __str__(self):
            return self.name
    
class Restaurant(models.Model):
    name = models.CharField(max_length=100, verbose_name="restaurant_name", null=False)
    address = models.CharField(max_length=200, verbose_name="restaurant_address", null=False)
    open_close_time = models.TextField(max_length=1000, verbose_name="open_close_time", null=True)
    image = models.ImageField(upload_to="", default='media/default_image.jpeg')
    phone = models.CharField(max_length=20, verbose_name="phone")
    map_link = models.URLField(max_length=200)
    latitude = models.FloatField(max_length=100, null=False)
    longitude= models.FloatField(max_length=100, null=False)
    koogle_ranking = models.IntegerField(verbose_name="koogle_ranking")
    reservation = models.BooleanField(verbose_name="reservation", default=False)
    reservation_link = models.URLField(verbose_name="reservation_url", null=True, blank=True)

    def clean(self):
        if self.reservation and not self.reservation_link:
            raise ValidationError("Reservation link is required when reservation is true.")
    
    reservation_link = models.URLField(verbose_name="reservation_url", null=True,blank=None)
    def __str__(self):
        return self.name

class Menu_Detail(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(null=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    content = models.TextField(max_length=1000, verbose_name="menu_detail_content")
    def __str__(self):
        return f'{self.name} is in menu'
    
class Menu(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    menu_detail = models.ForeignKey(Menu_Detail, on_delete=models.CASCADE)
    def __str__(self):
        return f'{self.menu_detail.name} is in {self.restaurant.name}menu'

class Restaurant_Food(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name="restaurant_food_restaurant")
    food = models.ForeignKey(Food, on_delete=models.CASCADE, related_name="restaurant_food_food")
    
    def __str__(self):
        return f'{self.food.name} is in {self.restaurant.name}'



