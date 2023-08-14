from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('api/signup/', SignupView.as_view(), name='api-signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('countries/', CountriesListView.as_view(), name='countries-list'),
]