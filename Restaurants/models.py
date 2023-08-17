from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="category_name")
    def __str__(self):
        return self.name

    @classmethod
    def get_others_category(cls):
        instance, _ = cls.objects.get_or_create(name='그 외')
        return instance
    
class Food(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="food_category")
    name = models.CharField(max_length=100, verbose_name="Food_name")
    def __str__(self):
            return self.name
    
    @classmethod
    def get_others_food(cls):
        instance, _ = cls.objects.get_or_create(category=Category.get_others_category(), name='기타')
        return instance

    
class Restaurant(models.Model):
    name = models.CharField(max_length=100, verbose_name="restaurant_name", null=False)
    address = models.CharField(max_length=200, verbose_name="restaurant_address", null=False)

    image = models.ImageField(upload_to="restaurants/restaurant-main-img/", default='restaurants/restaurant/default_image.jpeg')
    phone = models.CharField(max_length=20, verbose_name="phone", null=True)

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
    open_time = models.TimeField(null=True, blank=True)
    close_time = models.TimeField(null=True, blank=True)
    last_order_time = models.TimeField(null=True, blank=True)
    break_start_time = models.TimeField(null=True, blank=True)
    break_end_time = models.TimeField(null=True, blank=True)

    @classmethod
    def update_restaurant_open_hours(cls, restaurant_instance, open_hours):
        print(f'update_restaurant_open_hours({str(restaurant_instance)}, {open_hours})')

        # existing: DB에 저장된 이 레스토랑의 영업시간
        existing = cls.objects.filter(restaurant=restaurant_instance)
        incoming = open_hours if open_hours is not None else []

        incoming_open_hours_instances = [] 

        # add or update with latest open hours
        for open_hours_of_day in incoming:
            # Search the QuerySet for a matching entry
            instance, _ = cls.objects.get_or_create(**open_hours_of_day, restaurant=restaurant_instance)
            incoming_open_hours_instances.append(instance)

        # delete if not in latest open hours
        for instance in existing:
            if instance not in incoming_open_hours_instances:
                instance.delete()

class Menu_Detail(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to="restaurants/restaurant-main-img/", default='restaurants/restaurant/default_image.jpg')
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
    def update_restaurant_menus(cls, restaurant_instance, menus):
        print(f'update_restaurant_menus({restaurant_instance}, {menus})')
        
        if not menus: menus = []

        latest_menu_detail_ids = []

        for detail in menus:
            menu_detail, _ = Menu_Detail.objects.get_or_create(**detail)
            cls.objects.get_or_create(
                restaurant=restaurant_instance, 
                menu_detail=menu_detail
            )

            latest_menu_detail_ids.append(menu_detail.id)
        
        existing = cls.objects.filter(restaurant=restaurant_instance)
        for menu in existing:
            if menu.menu_detail_id not in latest_menu_detail_ids:
                menu.delete()

class Restaurant_Food(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name="restaurant_food_restaurant")
    food = models.ForeignKey(Food, on_delete=models.CASCADE, related_name="restaurant_food_food")
    
    def __str__(self):
        return f'{self.food.name} is in {self.restaurant.name}'
    
    @classmethod
    def update_restaurant_foods(cls, restaurant_instance, foods_queryset):
        print(f'update_restaurant_foods({restaurant_instance}, {foods_queryset})')

        if len(foods_queryset) == 0:
            cls.objects.get_or_create(restaurant=restaurant_instance, food=Food.get_others_food())
            return

        for food in foods_queryset:
            cls.objects.get_or_create(
                restaurant = restaurant_instance, 
                food=food
            )

        existing = cls.objects.filter(restaurant=restaurant_instance)
        for restaurant_food in existing:
            if restaurant_food.food not in foods_queryset:
                restaurant_food.delete()