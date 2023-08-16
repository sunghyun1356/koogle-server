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
        'ENGINE': 'django.db.backends.mysql', # engine: mysql
        'NAME' : 'koogle', # DB Name
        'USER' : 'admin', # DB User
        'PASSWORD' : 'sunghyun1356', # Password
        'HOST': 'sunghyun1356.catymkthpwcp.ap-northeast-2.rds.amazonaws.com', # 생성한 데이터베이스 엔드포인트
        'PORT': '3306', # 데이터베이스 포트
        'OPTIONS':{
            'init_command' : "SET sql_mode='STRICT_TRANS_TABLES'"
        }
    }
}
STATIC_ROOT = BASE_DIR / 'static'