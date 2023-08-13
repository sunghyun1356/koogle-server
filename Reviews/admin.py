from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(Likes)
admin.site.register(Review)
admin.site.register(Review_Likes)
admin.site.register(Likes_Restaurant)
admin.site.register(OpenHours)

