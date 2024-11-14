from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView

from . import views

urlpatterns = [
    path('register-otp/', views.RegisterTokenApiView.as_view(), name='register-otp'),
    path('login-otp/', views.LoginTokenApiView.as_view(), name='login-otp'),
    path('register/', views.RegisterApiView.as_view(), name='register'),
    path('user-login/', views.LoginApiView.as_view(), name='user-login'),
    path('admin-login/', TokenObtainPairView.as_view(), name='admin-login'),
]