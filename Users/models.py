from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
import boto3
# Create your models here.

class S3ImgUploader:
    def __init__(self, file):
        self.file = file

    def upload(self):
        s3_client = boto3.client(
            's3',
            aws_access_key_id     = settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key = settings.AWS_SECRET_ACCESS_KEY
        )
        url = 'img'+'/'+uuid.uuid1().hex
        
        s3_client.upload_fileobj(
            self.file, 
            "bucket_name", 
            url, 
            ExtraArgs={
                "ContentType": self.file.content_type
            }
        )
        return url


class UserManager(BaseUserManager):
    def create_user(self, username,password=None,**extra_fields):

        user = self.model(username=username,**extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user
    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True')
        extra_fields.setdefault('country', None)  # Set country to None for superuser

        return self.create_user(username, password, **extra_fields)

        
class Country(models.Model):
    name = models.CharField(max_length=100, verbose_name="country_name")
    def __str__(self):
        return self.name
    
class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=255, unique=True, null=False)
    country = models.ForeignKey(Country,on_delete=models.CASCADE, related_name='user_country',null=True)
    is_staff = models.BooleanField(default=False)
    last_login = models.DateTimeField(auto_now=True)
    objects = UserManager()
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []
    def __str__(self):
        return self.username