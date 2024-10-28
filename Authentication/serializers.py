from django.contrib.auth import authenticate
from rest_framework import serializers, status
from django.utils import timezone
from rest_framework.response import Response
from datetime import timedelta
from .models import User, EmailOTP ,Register_user 
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
    
      try:
          User.objects.get(email= attrs['email'])
      except:
         raise serializers.ValidationError({'error':'Email already exists'})
      
    print(1)
    def otp(self, attrs):
        otp = random.randint(1000, 9999)
        User.otp = otp
        print(2)
        send_verify_mail(attrs['email'],otp)
        return {'message' : 'OTP sent on email'}


class VerifyRegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.IntegerField()
    
    def validate(self, data):
        try:
            user = Register_user.objects.get(email = data['email'])
        except:
            raise serializers.ValidationError({"error":" Generate OTP"})
        if user.otp != data['otp']:
            raise serializers.ValidationError({'error':'Invalid OTP'})
     
        data['instance'] = user
        return data

    def create(self, data):
        obj = User.objects.create(
            email = data['email'],
            password = (data['password']),
        )
        data['instance'].delete()
        User.save()
        return data
          

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
    