from rest_framework import serializers, status
from rest_framework.generics import *
from Authentication.serializers import *
from rest_framework.permissions import AllowAny, IsAuthenticated 
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import User
  
class SendOTP(CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = SendOTPSerializer
    
class VerifyOTP(APIView):
    permission_classes = [AllowAny]
    serializer_class = VerifyotpSerializer
    
    def post(self, request, *args, **kwargs):
        serializer = VerifyotpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
 
    
class RegisterAPIView(CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class= RegisterSerializer
    
class LoginAPIView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
      
  