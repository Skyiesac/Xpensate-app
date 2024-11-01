from rest_framework import serializers, status
from rest_framework.generics import *
from Authentication.serializers import *
from rest_framework.permissions import AllowAny, IsAuthenticated 
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import User
{
"email":"skyyyy1y@gmail.com",
"password":"skyispretty"
}
    
class RegisterAPIView(CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class= RegisterSerializer
    
class LoginAPIView(APIView):
   permission_classes = [AllowAny]
   print(4)
   def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data = request.data)
        serializer.is_valid(raise_exception=True)
        print(5)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)

class VerifyOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = VerifyOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class ForgetPassword(APIView):
    permission_classes = [AllowAny]
    def post(self, request, *args, **kwargs):
        serializer = ForgetPassSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    
class ResetPassView(UpdateAPIView):
    permission_classes = [AllowAny]
    serializer_class = ResetPassSerializer
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'messsage':['Password changed successfully']}, status=status.HTTP_200_OK)
