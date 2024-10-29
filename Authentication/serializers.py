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
      if attrs['password'] is None:
           raise serializers.ValidationError({"password": "Password should not be blank"})
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


class VerifyOTPSerializer(serializers.Serializer):
    email= serializers.CharField()
    otp = serializers.IntegerField()
    
    def validate(self, data):
        try:
          user= EmailOTP.objects.get(email= data['email'])
        except:
          raise serializers.ValidationError({'error':'Invalid user'})
        user= EmailOTP.objects.get(email= data['email'])
        otph = user.otp
        print(otph)
        if otph != data['otp']:
            raise serializers.ValidationError({'error':'Invalid OTP'})
        if user.forgot:
            self.forgot_us(data)
        else:
            self.create_us(data)
        return {
            "message" : "verified" }
        
    #when otp is to register    
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
          
    #when otp is to reset password
    def forgot_us(self , data):
        EmailOTP.objects.filter(email=data['email']).delete()
        return{
            'message' : 'User verified successfully'
        }

class LoginSerializer(serializers.Serializer):
    
    email = serializers.EmailField(max_length=255)
    password = serializers.CharField(write_only=True)
    
    def validate(self, data):
        email = data['email']
        email = normalize_email(email)
        
        user = User.objects.filter(email = email).exists()
        if not user:
         raise serializers.ValidationError({"error":"Invalid user"})
        
        
        usert = authenticate(email=email,password=data['password'] )
        
        if not usert:
            raise serializers.ValidationError({"error":"Incorrect Credentials"})
        data['user']=usert
        return data
    
class ForgetPassSerializer(serializers.Serializer):
    email = serializers.EmailField(write_only = True)

    def validate(self, data):
       user= User.objects.filter(email=data['email']).exists()
       if not user:
           raise serializers.ValidationError({"error":"User doesn't exist"})
       otpto= self.sendotp( data)
       EmailOTP.objects.update_or_create(
            email= data['email'],
            defaults={'otp':otpto},
            forgot =True
        )
       return data
        
    def sendotp(self, attrs):
        otpto = random.randint(1000, 9999)
        otp_for_reset(attrs['email'], otpto)
        
        return otpto
    

class ResetPassSerializer(serializers.Serializer):
     email= serializers.EmailField()
     new_password = serializers.CharField(min_length=8)
     confirm_password = serializers.CharField(min_length=8)

     def validate(self, attrs):
        if attrs['new_password'] is None:
           raise serializers.ValidationError({"password": "Password should not be blank"})
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        try:
          user = User.objects.get(email=attrs['email'])
        except:
            raise serializers.ValidationError({"error": "User with this email does not exist."})
        attrs['user']=user
        return attrs
        
     def save(self):
            user = self.validated_data['user']
            user.set_password(self.validated_data['new_password'])
            user.save()
            return user 

