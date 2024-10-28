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
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)  

class VerifyRegisterView(CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = VerifyRegisterSerializer

class ForgetPassword(UpdateAPIView):
    permission_classes = [AllowAny]
    serializer_class = ForgetPassSerializer
    

# class ResetPassView(UpdateAPIView):
#     permission_classes = [AllowAny]
#     serializer_class = ResetPassSerializer
    
#     def patch(self, request, *args, **kwargs):
#         self.update(request,*args, **kwargs)
#         return Response({'messsage':['Password changed successfully']}, status=status.HTTP_200_OK)
