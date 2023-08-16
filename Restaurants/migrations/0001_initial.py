# Generated by Django 4.2.4 on 2023-08-16 05:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='category_name')),
                ('image', models.ImageField(default='restaurants/category/default_image.jpeg', upload_to='restaurants/category-img/')),
            ],
        ),
        migrations.CreateModel(
            name='Food',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Food_name')),
                ('image', models.ImageField(default='restaurants/food/default_image.jpeg', upload_to='restaurants/food-img/')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='food_category', to='Restaurants.category')),
            ],
        ),
        migrations.CreateModel(
            name='Menu_Detail',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('image', models.ImageField(null=True, upload_to='')),
                ('price', models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True)),
                ('content', models.TextField(blank=True, max_length=1000, null=True, verbose_name='menu_detail_content')),
            ],
        ),
        migrations.CreateModel(
            name='Restaurant',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='restaurant_name')),
                ('address', models.CharField(max_length=200, verbose_name='restaurant_address')),
                ('image', models.ImageField(default='restaurants/restaurant/default_image.jpeg', upload_to='restaurants/restaurant-main-img/')),
                ('phone', models.CharField(max_length=20, verbose_name='phone')),
                ('map_link', models.URLField()),
                ('latitude', models.FloatField(max_length=100)),
                ('longitude', models.FloatField(max_length=100)),
                ('koogle_ranking', models.IntegerField(default=0, verbose_name='koogle_ranking')),
                ('reservation', models.BooleanField(default=False, verbose_name='reservation')),
                ('reservation_link', models.URLField(blank=True, null=True, unique=True, verbose_name='reservation_url')),
            ],
        ),
        migrations.CreateModel(
            name='Restaurant_Food',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('food', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='restaurant_food_food', to='Restaurants.food')),
                ('restaurant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='restaurant_food_restaurant', to='Restaurants.restaurant')),
            ],
        ),
        migrations.CreateModel(
            name='OpenHours',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('day', models.CharField(max_length=15, verbose_name='day of the week')),
                ('open_time', models.TimeField()),
                ('close_time', models.TimeField()),
                ('last_order_time', models.TimeField(blank=True, null=True)),
                ('break_start_time', models.TimeField(blank=True, null=True)),
                ('break_end_time', models.TimeField(blank=True, null=True)),
                ('restaurant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='open_hours', to='Restaurants.restaurant')),
            ],
        ),
        migrations.CreateModel(
            name='Menu',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('menu_detail', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Restaurants.menu_detail')),
                ('restaurant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Restaurants.restaurant')),
            ],
        ),
    ]
