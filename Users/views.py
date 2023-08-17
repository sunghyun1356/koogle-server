from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate, logout
from django.conf import settings
from django.shortcuts import render
from django.shortcuts import get_object_or_404

from rest_framework import generics
from rest_framework import serializers
from .serializers import UserRegisterSerializer

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.contrib.auth import get_user_model

import jwt # PyJWT 설치 해야함

from .models import Country
from django.contrib.sessions.backends.db import SessionStore
from django.contrib.auth import get_user_model

User = get_user_model()

User = get_user_model()
# jwt로 된건가?


class CountriesListView(APIView):
    def get(self, request):
        countries = Country.objects.all()
        return render(request, 'signup_form.html', {'countries': countries})
        # countries = Country.objects.all().values_list('name', flat=True)
        # return Response(countries)
    


class LogoutView(APIView):
    def post(self, request):
        logout(request)
        return Response({'message': 'Logged out.'})

# 회원가입
class UserRegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    
# 로그인
class CustomTokenObtainPairView(TokenObtainPairView):
    pass  

