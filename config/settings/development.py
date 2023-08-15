from .base import *


DEBUG = False
ALLOWED_HOSTS = [
    '*'
]

DJANGO_APPS + []

PROJECT_APPS + []

THIRD_PARTY_APPS + [
    'debug_toolbar'
]

INSTALLED_APPS = DJANGO_APPS + PROJECT_APPS + THIRD_PARTY_APPS

# 데이터베이스는 AWS RDS Mysql 사용 했습니다.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
		'NAME': 'tealog',
        'USER': 'root',
        'PASSWORD': '1',
        'HOST': 'svc.sel3.cloudtype.app',
        'PORT': '30186',
        'OPTIONS':{
            'init_command' : "SET sql_mode='STRICT_TRANS_TABLES'"
        }
    }
}
STATIC_ROOT = BASE_DIR / 'static'