# Generated by Django 4.2.4 on 2023-08-16 05:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('Restaurants', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Likes',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('likes', models.CharField(max_length=100, verbose_name='likes_type')),
            ],
        ),
        migrations.CreateModel(
            name='Likes_Restaurant',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField(max_length=1000, verbose_name='content')),
                ('image_1', models.ImageField(default='reviews/review_default-img', null=True, upload_to='reviews/review-img')),
                ('image_2', models.ImageField(default='reviews/review_default-img', null=True, upload_to='reviews/review-img')),
                ('image_3', models.ImageField(default='reviews/review_default-img', null=True, upload_to='reviews/review-img')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('koogle', models.IntegerField(default=0, null=True, verbose_name='koogle')),
                ('star', models.IntegerField(verbose_name='star')),
                ('restaurant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='review_restaurant', to='Restaurants.restaurant')),
            ],
        ),
        migrations.CreateModel(
            name='Review_Likes',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('likes', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='likes_review_likes', to='Reviews.likes')),
                ('review', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='review_review_likes', to='Reviews.review')),
            ],
        ),
    ]
