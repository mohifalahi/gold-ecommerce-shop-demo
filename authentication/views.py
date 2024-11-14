from rest_framework import generics, status
from rest_framework.response import Response

from .models import User
from .serializers import *
from .validators import *


class RegisterTokenApiView(generics.GenericAPIView):
    serializer_class = RegisterTokenSerializer

    def post(self, request):
        try:
            serializer = self.serializer_class(request=request, data=request.data)
            serializer.is_valid(raise_exception=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response({'error': e.detail}, status=status.HTTP_400_BAD_REQUEST)
        

class LoginTokenApiView(generics.GenericAPIView):
    serializer_class = LoginTokenSerializer

    def post(self, request):
        try:
            serializer = self.serializer_class(request=request, data=request.data)
            serializer.is_valid(raise_exception=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response({'error': e.detail}, status=status.HTTP_400_BAD_REQUEST)
    

class RegisterApiView(generics.GenericAPIView):
    serializer_class = UserRegisterSerializer

    def post(self, request):
        request_data = request.data
        serializer = self.serializer_class(data=request_data)
        serializer.is_valid(raise_exception=True)
        mobile = serializer.validated_data.get('mobile')
        user, created = User.objects.get_or_create(mobile=mobile)
        tokens = serializer.create_jwt_token(user)
        return Response(tokens, status=status.HTTP_200_OK)


class LoginApiView(generics.GenericAPIView):
    serializer_class = UserLoginSerializer

    def post(self, request):
        request_data = request.data
        serializer = self.serializer_class(data=request_data)
        serializer.is_valid(raise_exception=True)
        mobile = serializer.validated_data.get('mobile')
        user = User.objects.get(mobile=mobile)
        tokens = serializer.create_jwt_token(user)
        return Response(tokens, status=status.HTTP_200_OK)

