from django.contrib.auth import authenticate
from rest_framework import serializers, status
from django.utils import timezone
from rest_framework.response import Response
from datetime import timedelta
from .models import User, Register_user 
from django.core.validators import MinLengthValidator
from .utils import *
import random

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Register_user
        fields = ['email', 'password', 'confirm_password']

    def validate(self , attrs):
      if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"password": "Password aren't matching."})
      self.otpsend(attrs)
      return attrs
    
    print(1)
    def otpsend(self, attrs):
        otpto = random.randint(1000, 9999)
        send_verify_mail(attrs['email'],otpto)
        user = Register_user.objects.filter(
            email= attrs['email']).update(otp=otpto)
       
        return {'message' : 'OTP sent on email'}


class VerifyRegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.IntegerField()
    
    def validate(self, data):
        try:
            user = Register_user.objects.get(email=data['email'])
        except Register_user.DoesNotExist:
            raise serializers.ValidationError({"error": "User does not exist."})

        if user.otp != data['otp']:
            raise serializers.ValidationError({'error':'Invalid OTP'})
     
        data['instance'] = user
        return data

    def create(self, data):
        user = Register_user.objects.get(email = data['email'])
        User.objects.create(
            email = data['email'],
            password = user.password )
        User.save()
        data['instance'].delete()
        return User
          

class LoginSerializer(serializers.Serializer):
    
    email = serializers.EmailField(max_length=255, write_only=True)
    password = serializers.CharField(write_only=True, min_length=8)
    tokens = serializers.JSONField(read_only=True)
    
    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        email = normalize_email(email)
        
        if not User.objects.filter(email = email).exists():
         raise serializers.ValidationError({"error":"Invalid user"})
      
        user = authenticate(email=email,password=password )
        
        if not user:
            raise serializers.ValidationError({"error":"Incorrect Credentials"})

        return {
            'message': "Login Successful",
            'tokens': user.get_tokens,
        }
    