from rest_framework import serializers, status
from rest_framework.generics import *
from Authentication.serializers import *
from rest_framework.permissions import AllowAny, IsAuthenticated 
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import User

    
class RegisterAPIView(CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class= RegisterSerializer
    
class LoginAPIView(APIView):
   permission_classes = [AllowAny]

   def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data = request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        return Response({ **{'message' : ['Login Successful']}, **serializer.data}, status=status.HTTP_200_OK)

class VerifyOTPView(CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = VerifyOTPSerializer

class ForgetPassword(CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = ForgetPassSerializer
    

class ResetPassView(UpdateAPIView):
    permission_classes = [AllowAny]
    serializer_class = ResetPassSerializer
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'messsage':['Password changed successfully']}, status=status.HTTP_200_OK)
