import random

from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from .models import IP, TempUser, User
from .utils import *
from .validators import *

User = get_user_model()

def handle_otp_generation(mobile):
    otp = random.randint(1000, 10000)
    send_sms(receptor=mobile, token=otp)
    TempUser.objects.filter(mobile=mobile).delete()
    TempUser.objects.create(mobile=mobile, token=otp)


def check_ip_validation(self):
    request_ip = get_ip(request=self.request)
    ip_obj = IP.objects.filter(ip=request_ip)
    if not ip_obj:
        IP.objects.create(ip=request_ip)
        return True
    else:
        can_access, message = ip_obj[0].can_access()
        if can_access:
            return True
        else:
            raise ValidationError({'error': message})


class RegisterTokenSerializer(serializers.ModelSerializer):
    mobile = serializers.CharField(max_length=11)

    def __init__(self, request=None, **kwargs):
        self.request = request
        super().__init__(**kwargs)

    class Meta:
        model = User
        fields = ['mobile']

    def validate(self, attrs):

        check_ip_validation(self)
        mobile = attrs.get('mobile', None)

        user_query = User.objects.filter(mobile=mobile)

        if user_query:
            raise ValidationError('this user is already registered.')
        else:
            handle_otp_generation(mobile)
        
        return {
            'mobile': mobile
        }
        

class LoginTokenSerializer(serializers.ModelSerializer):
    mobile = serializers.CharField(max_length=11)

    def __init__(self, request=None, **kwargs):
        self.request = request
        super().__init__(**kwargs)

    class Meta:
        model = User
        fields = ['mobile']

    def validate(self, attrs):

        check_ip_validation(self)
        mobile = attrs.get('mobile', None)

        user_query = User.objects.filter(mobile=mobile)

        if not user_query:
            raise ValidationError('this user does not exist.')
        else:
            handle_otp_generation(mobile)
        
        return {
            'mobile': mobile
        }


class UserRegisterSerializer(serializers.ModelSerializer):
    token = serializers.IntegerField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['mobile', 'token']
        extra_kwargs = {
            'mobile': {'required': True},
            'token': {'required': True},
        }

    def validate(self, attrs):
        mobile = attrs.get('mobile', '')
        token = attrs.get('token', '')
        temp_user_query = TempUser.objects.filter(mobile=mobile)

        if not temp_user_query:
            raise ValidationError('you must first take a token.')
            
        if temp_user_query[0].is_expired():
            raise ValidationError('your last token is expired.')
        
        if temp_user_query[0].token != token:
            raise ValidationError('your token is wrong.')
    
        return attrs

    def create_jwt_token(self, user):
        # Generate JWT tokens for the user
        refresh = RefreshToken.for_user(user)
        return {
            'access': str(refresh.access_token),
        }


class UserLoginSerializer(serializers.ModelSerializer):
    mobile = serializers.CharField(max_length=11)
    token = serializers.IntegerField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['mobile', 'token']

    def validate(self, attrs):
        mobile = attrs.get('mobile', '')
        token = attrs.get('token', '')
        user_query = User.objects.filter(mobile=mobile)
        temp_user_query = TempUser.objects.filter(mobile=mobile)

        if not user_query:
            raise ValidationError('user does not exists.')
            
        if temp_user_query[0].is_expired():
            raise ValidationError('your last token is expired.')
        
        if temp_user_query[0].token != token:
            raise ValidationError('your token is wrong.')
    
        return attrs

    def create_jwt_token(self, user):
        # Generate JWT tokens for the user
        refresh = RefreshToken.for_user(user)
        return {
            'access': str(refresh.access_token),
        }
