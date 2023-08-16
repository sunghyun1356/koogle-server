from .base import *


DEBUG = True
ALLOWED_HOSTS = [
    '*'
]

DJANGO_APPS + []

PROJECT_APPS + []

THIRD_PARTY_APPS + []

INSTALLED_APPS = DJANGO_APPS + PROJECT_APPS + THIRD_PARTY_APPS

# 데이터베이스는 AWS RDS Mysql 사용 했습니다.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # engine: mysql
        'NAME' : 'BASE_DIR', # DB Name
    }
}

STATIC_ROOT = BASE_DIR / 'static'