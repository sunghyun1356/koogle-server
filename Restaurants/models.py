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
    koogle_ranking = models.IntegerField(verbose_name="koogle_ranking", default=0)
    reservation = models.BooleanField(verbose_name="reservation", default=False)
    reservation_link = models.URLField(verbose_name="reservation_url", null=True, blank=True, unique=True)
    def __str__(self):
        return self.name   

class OpenHours(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='open_hours')
    day = models.CharField(verbose_name='day of the week', max_length=15) # ex. Mon, Tue, Wed
    open_time = models.TimeField()
    close_time = models.TimeField()
    last_order_time = models.TimeField(null=True, blank=True)
    break_start_time = models.TimeField(null=True, blank=True)
    break_end_time = models.TimeField(null=True, blank=True)

    @classmethod
    def compare_hours(cls, lhs, rhs):
        open_hour_fields = ['day'] + [field.name for field in cls._meta.get_fields() if field.name not in ['id', 'restaurant', 'day']]

        for key in open_hour_fields:
            if lhs.get(key, None) != getattr(rhs, key, None):
                return 1 if lhs.get(key, None) < getattr(rhs, key, None) else -1
        
        return 0

    @classmethod
    def update_restaurant_open_hours(cls, restaurant_obj, open_hours):
        try: 
            existing = cls.objects.filter(restaurant=restaurant_obj).order_by('day')
        except cls.DoesNotExist:
            existing = []

        try:
            incoming = sorted(open_hours, key=lambda x: x['day'])
        except TypeError:
            incoming = []

        print('after try-except')

        to_add = [] # OpenHour object to add
        to_vanish = [] # OpenHour model instances to remove
        i = 0
        j = 0

        while (i < len(incoming) and j < len(existing)):
            cmp = cls.compare_hours(incoming[i], existing[j])
            if cmp == 0:
                i = i + 1
                j = j + 1
            elif cmp > 0:
                to_vanish.append(existing[j])
                j = j + 1
            else:
                to_add.append(incoming[i])
                i = i + 1
        while (i < len(incoming)):
            to_add.append(incoming[i])
            i = i + 1
        while (j < len(existing)):
            to_vanish.append(existing[j])
            j = j + 1
        
        print('after comparison')

        for open_hour in to_vanish:
            open_hour.delete()

        print('after deletion')

        for open_hour in to_add:
            cls.objects.get_or_create(restaurant=restaurant_obj, **open_hour)
        
        print('after addition')


class Menu_Detail(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(null=True)
    price = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    content = models.TextField(max_length=1000, verbose_name="menu_detail_content", blank=True, null=True)
    def __str__(self):
        return f'{self.name}({self.price}원) {str(self.content)[:10]}...'
    
class Menu(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    menu_detail = models.ForeignKey(Menu_Detail, on_delete=models.CASCADE)
    def __str__(self):
        return f'{self.menu_detail.name} is in {self.restaurant.name}menu'
    
    @classmethod
    def compare_menus(cls, lhs, rhs):
        menu_detail_fields = ['name'] + [field.name for field in Menu_Detail._meta.get_fields() if field.name not in ['id', 'name', 'image']]

        for key in menu_detail_fields:
            if lhs.get(key, None) != getattr(rhs, key, None):
                return 1 if lhs.get(key, None) < getattr(rhs, key) else -1
        
        return 0

    @classmethod
    def update_restaurant_menus(cls, restaurant_obj, menus):
        print(f'update_restaurant_menus({restaurant_obj}, {menus})')

        try: 
            existing_menus = cls.objects.filter(restaurant=restaurant_obj).select_related('menu_detail')
            existing_menus = existing_menus.order_by('menu_detail__name')
            existing = [m.menu_detail for m in existing_menus]
        except cls.DoesNotExist:
            existing = []

        try: 
            incoming = sorted(menus, key=lambda x: x['name'])
        except TypeError:
            incoming = []

        print(f'incoming: {incoming}')
        print(f'existing: {existing}')

        to_add = [] # Menu_Detail objects to add
        to_vanish = [] # Menu_Detail model instances to remove
        i = 0
        j = 0

        while (i < len(incoming) and j < len(existing)):
            cmp = cls.compare_menus(incoming[i], existing[j])
            if cmp == 0:
                i = i + 1
                j = j + 1
            elif cmp > 0:
                to_vanish.append(existing[j])
                j = j + 1
            else:
                to_add.append(incoming[i])
                i = i + 1
        while (i < len(incoming)):
            to_add.append(incoming[i])
            i = i + 1
        while (j < len(existing)):
            to_vanish.append(existing[j])
            j = j + 1

        for menu_detail in to_vanish:
            menu_detail.delete()
        for menu_detail in to_add:
            menu_detail_obj, _ = Menu_Detail.objects.get_or_create(**menu_detail)
            cls.objects.get_or_create(restaurant=restaurant_obj, menu_detail=menu_detail_obj)


class Restaurant_Food(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name="restaurant_food_restaurant")
    food = models.ForeignKey(Food, on_delete=models.CASCADE, related_name="restaurant_food_food")
    
    def __str__(self):
        return f'{self.food.name} is in {self.restaurant.name}'



