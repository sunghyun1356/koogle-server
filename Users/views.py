from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate, logout
from django.conf import settings
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from rest_framework import generics
from serializers import UserRegisterSerializer
from jwt import Tok
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

import jwt # PyJWT 설치 해야함
from .models import Country
from django.contrib.sessions.backends.db import SessionStore
from django.contrib.auth import get_user_model
User = get_user_model()
# jwt로 된건가?

# 회원가입
class UserRegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    
# 로그인
class CustomTokenObtainPairView(TokenObtainPairView):
    pass  