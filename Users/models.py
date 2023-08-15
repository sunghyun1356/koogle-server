from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

# Create your models here.

class UserManager(BaseUserManager):
    def create_user(self, email,password=None,**extra_fields):
        if not email:
            raise ValueError('The Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email,**extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    def create_superuser(self, email, country=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True')
        
        return self.create_user(email, password, **extra_fields)

        
class Country(models.Model):
    name = models.CharField(max_length=100, verbose_name="country_name")
    def __str__(self):
        return self.name
    
class User(AbstractBaseUser, PermissionsMixin):
    name = models.CharField(max_length=255, unique=True, null=False)
    country = models.ForeignKey(Country,on_delete=models.CASCADE, related_name='user_country',null=True )
    is_staff = models.BooleanField(default=False)
    email = models.EmailField(unique=True)
    last_login = models.DateTimeField(auto_now=True)
    objects = UserManager()
    USERNAME_FIELD = 'name'
    REQUIRED_FIELDS = []
    def __str__(self):
        return self.name