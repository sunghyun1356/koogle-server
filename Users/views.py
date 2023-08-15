from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate, logout
from django.conf import settings
from django.shortcuts import render
from django.shortcuts import get_object_or_404

import jwt # PyJWT 설치 해야함
from .models import User
from .models import Country
from django.contrib.sessions.backends.db import SessionStore


# jwt로 된건가?

class CountriesListView(APIView):
    def get(self, request):
        countries = Country.objects.all()
        return render(request, 'signup_form.html', {'countries': countries})
        # countries = Country.objects.all().values_list('name', flat=True)
        # return Response(countries)
    
class SignupView(APIView):
    def get(self, request):
        countries = Country.objects.all()
        context = {'countries': countries}
        return render(request, 'signup_form.html', context)
    
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        country = request.data.get('country')
        email = request.data.get('email')
        hashed_password = make_password(password)
        country_instance = get_object_or_404(Country, name=country)

        user = User.objects.create(username=username, password=hashed_password, email=email, country=country_instance)

        payload = {'user_id': user.id, 'username': user.username, 'country': country_instance.name} # type: ignore
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
        
        # 회원가입이 완료되었다는 문구, 메인페이지로 가기 버튼 있는 페이지로
        context = {'username': username, 'country': country}
        return render(request, 'signup_complete.html', context)

class LoginView(APIView):
    def get(self, request):
        return render(request, 'login.html')
    
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(request, username=username, password=password)
        print(user)
        if user:
            payload = {'user_id': user.id, 'username': user.username, 'country': user.country} # type: ignore
            token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
            return Response({'token': token})
        else:
            return Response({'message': 'Login failed.'}, status=status.HTTP_401_UNAUTHORIZED)

class LogoutView(APIView):
    def post(self, request):
        logout(request)
        return Response({'message': 'Logged out.'})