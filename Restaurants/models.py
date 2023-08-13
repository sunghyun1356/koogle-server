from django.db import models
from enum import unique
from rest_framework.exceptions import ValidationError
# Create your models here.


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="category_name")
    image = models.ImageField(upload_to="restaurants/category-img/", default='restaurants/category/default_image.jpeg')
    def __str__(self):
        return self.name
    
class Food(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="food_category")
    name = models.CharField(max_length=100, verbose_name="Food_name")
    image = models.ImageField(upload_to="restaurants/food-img/", default='restaurants/food/default_image.jpeg')
    def __str__(self):
            return self.name
    
class Restaurant(models.Model):
    name = models.CharField(max_length=100, verbose_name="restaurant_name", null=False)
    address = models.CharField(max_length=200, verbose_name="restaurant_address", null=False)

    image = models.ImageField(upload_to="restaurants/restaurant-main-img/", default='restaurants/restaurant/default_image.jpeg')
    phone = models.CharField(max_length=20, verbose_name="phone")
    map_link = models.URLField(max_length=200)
    latitude = models.FloatField(max_length=100, null=False)
    longitude= models.FloatField(max_length=100, null=False)
    koogle_ranking = models.IntegerField(verbose_name="koogle_ranking")
    reservation = models.BooleanField(verbose_name="reservation", default=False)
    reservation_link = models.URLField(verbose_name="reservation_url", null=True, blank=True, unique=True)


class OpenHours(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='open_hours')
    day = models.CharField(verbose_name='day of the week', max_length=15) # ex. Mon, Tue, Wed
    open_time = models.TimeField()
    close_time = models.TimeField()

class Menu_Detail(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(null=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
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



