from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView

from . import views

urlpatterns = [
    path('generate-otp/', views.GenerateTokenApiView.as_view(), name='generate-otp'),
    path('register/', views.RegisterApiView.as_view(), name='register'),
    path('user-login/', views.LoginApiView.as_view(), name='user-login'),
    path('admin-login/', TokenObtainPairView.as_view(), name='admin-login'),
]