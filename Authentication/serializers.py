from django.contrib.auth import authenticate
from rest_framework import serializers, status
from django.utils import timezone
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta
from .models import User, Register_user , EmailOTP
from django.core.validators import MinLengthValidator
from .utils import *
import random
from django.contrib.auth.hashers import make_password

class RegisterSerializer(serializers.Serializer):
    email= serializers.CharField(write_only = True)
    password = serializers.CharField(write_only= True)
    confirm_password = serializers.CharField(write_only= True)
    message= serializers.CharField(read_only=True)
    #  message= serializers.CharField(read_only=True)
    def validate(self , attrs):
      if attrs['password'] != attrs['confirm_password']:
           raise serializers.ValidationError({"password": "Passwords aren't matching."})
      if not strong_pass(attrs['password']):
          raise serializers.ValidationError({"password": "Password is not strong enough."})
      if User.objects.filter(email=attrs['email']):
         raise serializers.ValidationError({"Error":"User with this email already exists"})
      if Register_user.objects.filter(email=attrs['email']):
        Register_user.objects.get(email=attrs['email']).delete()
        EmailOTP.objects.get(email=attrs['email']).delete()

      otpto = self.otpsend(attrs)
      EmailOTP.objects.create(
            email= attrs['email'],
            otp=otpto
        )
      return attrs
    
    def create(self, validated_data):
        # Removing confirm_password
        validated_data.pop('confirm_password', None)
        # Hash the password
        validated_data['password'] = make_password(validated_data['password'])
        
        user = Register_user.objects.create(**validated_data)
        return user

    def otpsend(self, attrs):
        otpto = random.randint(1000, 9999)
        send_verify_mail(attrs['email'], otpto)
        
        return otpto


class VerifyOTPSerializer(serializers.Serializer):
    email= serializers.CharField(write_only = True)
    otp = serializers.IntegerField(write_only= True)
    message= serializers.CharField(read_only=True)
    tokens = serializers.JSONField(read_only=True)
    def validate(self, data):
        try:
          user= EmailOTP.objects.get(email=data['email'])
        except:
          raise serializers.ValidationError({'error':'Invalid user'})
        user= EmailOTP.objects.get(email= data['email'])
        print(1)
        otph = user.otp
        if otph != data['otp']:
            raise serializers.ValidationError({'error':'Invalid OTP'})
        if user.otp_created_at + timedelta(minutes=5)< timezone.now() :
           raise serializers.ValidationError({'error':'OTP expired, Resend OTP'})
        return self.create_us(data)
        
        
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
            'message': "User created successfully",
            "tokens": user.get_tokens()
        }
        
    def resend(self, attrs):
        otpto= random.randint(1000,9999)
        user= EmailOTP.objects.update_or_create(
            email= attrs['email'],
            otp=otpto
        )
       
        send_verify_mail(attrs['email'], otpto)
        
        return{
            'message':'OTP Resent'
        }

class LoginSerializer(serializers.Serializer):
    message= serializers.CharField(read_only=True)
    email = serializers.EmailField(max_length=255)
    password = serializers.CharField(write_only=True)
    tokens = serializers.JSONField(read_only=True)

    def validate(self, data):
       
        email = data['email']
        email = normalize_email(email)
        try:
         user = User.objects.get(email=email)
        except:
         raise serializers.ValidationError({"error":"Invalid user"})
        
        usert = authenticate(email=email,password=data['password'] )
        
        if not usert:
            raise serializers.ValidationError({"error":"Incorrect Credentials"})
       
        
        # data['message']= "Login Successful",
        # data['tokens']= user.get_tokens(),
        # return data
        return {
            'message': "Login Successful",
            'tokens': user.get_tokens(),
        }

    
class ForgetPassSerializer(serializers.Serializer):
    email = serializers.EmailField(write_only = True)
    message= serializers.CharField(read_only=True)
    def validate(self, data):
       user= User.objects.filter(email=data['email']).exists()
       if not user:
           raise serializers.ValidationError({"error":"User doesn't exist"})
       otpto= self.sendotp( data)
       EmailOTP.objects.update_or_create(
            email= data['email'],
            defaults={'otp':otpto}
        )
       return data
        
    def sendotp(self, attrs):
        otpto = random.randint(1000, 9999)
        otp_for_reset(attrs['email'], otpto)
        
        return otpto
   
class verifyforgetserializer(serializers.Serializer):
     email= serializers.EmailField()
     otp = serializers.IntegerField()
     def validate(self,attrs):
        try:
           User.objects.get(email=attrs['email'])
        except:
           raise serializers.ValidationError({"error": "User with this email does not exist."})

        try:
         userotp= EmailOTP.objects.get(email= attrs['email'])
        except:  
          raise serializers.ValidationError({"error": "This OTP is not valid"})
        otph = userotp.otp
        if otph != attrs['otp']:
                raise serializers.ValidationError({'error':'Invalid OTP'})
        if userotp.otp_created_at + timedelta(minutes=5)< timezone.now() :
                raise serializers.ValidationError({'error':'OTP expired, Resend OTP'})
        attrs['userotp'] = userotp
        return attrs

     def save(self):
            userotp = self.validated_data['userotp']
            userotp.forgot = True 
            userotp.save()
            return {'message': 'OTP verified successfully'}


         

class ResetPassSerializer(serializers.Serializer):
     email= serializers.EmailField()
     otp = serializers.IntegerField()
     new_password = serializers.CharField(min_length=8)
     message= serializers.CharField(read_only=True)

     def validate(self, attrs):
        if not strong_pass(attrs['new_password']):
            raise serializers.ValidationError({"password": "Password isn't strong enough."})
        try:
          user = User.objects.get(email=attrs['email'])
        except:
           raise serializers.ValidationError({"error": "User with this email does not exist."})

        try:
         userotp= EmailOTP.objects.get(email= attrs['email'], forgot=True)
        except:  
          raise serializers.ValidationError({"error": "This OTP is not either verified or valid"})
        attrs['user']=user
        
        return attrs
        #return validate(attrs)
        # new_pass = attrs['new_password']
        # User.objects.filter(email=attrs['email'])

     def save(self):
            user = self.validated_data['user']
            user.set_password(self.validated_data['new_password'])
            user.save()
            EmailOTP.objects.get(email = self.validated_data['email'] ).delete()
            return user 
