# Generated by Django 4.2.4 on 2023-08-12 15:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Restaurants', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='image',
            field=models.ImageField(default='restaurants/category/default_image.jpeg', upload_to='restaurants/category-img/'),
        ),
        migrations.AlterField(
            model_name='food',
            name='image',
            field=models.ImageField(default='restaurants/food/default_image.jpeg', upload_to='restaurants/food-img/'),
        ),
        migrations.AlterField(
            model_name='restaurant',
            name='image',
            field=models.ImageField(default='restaurants/restaurant/default_image.jpeg', upload_to='restaurants/restaurant-main-img/'),
        ),
    ]
