from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin,AbstractUser

# Create your models here.



    

class Country(models.Model):
    name = models.CharField(max_length=100, verbose_name="country_name")
    def __str__(self):
        return self.name
    
class User(AbstractUser):
    country = models.ForeignKey(Country,on_delete=models.CASCADE)
    is_staff = models.BooleanField(default=False, null=False)
    def __str__(self):
        return self.username