from django.contrib.auth import authenticate
from rest_framework import serializers, status
from django.utils import timezone
from rest_framework.response import Response
from datetime import timedelta
from .models import User, Register_user , EmailOTP
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
      otpto = self.otpsend(attrs)
      EmailOTP.objects.update_or_create(
            email= attrs['email'],
            otp=otpto
        )
      return attrs
   
    def otpsend(self, attrs):
        otpto = random.randint(1000, 9999)
        send_verify_mail(attrs['email'], otpto)
        
        return otpto


class VerifyRegisterSerializer(serializers.Serializer):
    email= serializers.CharField()
    otp = serializers.IntegerField()
    
    def validate(self, data):
        user= EmailOTP.objects.get(email= data['email'])
        otph = user.otp
        print(otph)
        if otph != data['otp']:
            raise serializers.ValidationError({'error':'Invalid OTP'})
        else:
            self.create_us( data)
            return {
            "message" : "verified" }
        
    def create_us(self, data):
        user, created = User.objects.get_or_create(
            email=data['email'],
            defaults={'password': Register_user.objects.get(email=data['email']).password}
        )
        if not user:
            raise serializers.ValidationError({'error': 'User with this email already exists.'})
        if created:
            user.set_password(user.password)  
            user.save()
        EmailOTP.objects.filter(email=data['email']).delete()
        Register_user.objects.filter(email= data['email']).delete()
        return {
            'message': 'User created successfully'
        }
          

class LoginSerializer(serializers.Serializer):
    
    email = serializers.EmailField(max_length=255)
    password = serializers.CharField(write_only=True)
    
    def validate(self, data):
        email = data['email']
        email = normalize_email(email)
        
        user = User.objects.filter(email = email).first()
        if not user:
         raise serializers.ValidationError({"error":"Invalid user"})
        
        print(f"Attempting to authenticate user: {email} password : {User.password}")
        user = authenticate(email=email,password=data['password'] )
        
        if not user:
            raise serializers.ValidationError({"error":"Incorrect Credentials"})
        
        return {
            'message': "Login Successful",
        }

class ForgetPassSerializer(serializers.Serializer):
    email = serializers.EmailField(write_only = True)

    def validate(self, email):
       user= User.objects.filter(email=email).exists()
       if not user:
           raise serializers.ValidationError({"error":"User doesn't exist"})
        
    def sendotp(self, attrs):
        otpto = random.randint(1000, 9999)
        otp_for_reset(attrs['email'], otpto)
        
        return { "message": "Email sent successfully"}
    
