from django.contrib.auth import authenticate
from rest_framework import serializers, status
from django.utils import timezone
from rest_framework.response import Response
from datetime import timedelta
from .models import User, EmailOTP
from .utils import *
import random

class RegisterSerializer(serializers.Serializer):
    
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True)
    def validate(self, attrs):
        email = normalize_email(attrs.get('email'))
        
        password = attrs.get('password')
        email_otp = attrs.get('email_otp')
        
        if User.objects.filter(email__iexact = email).exists():
            raise serializers.ValidationError({'error':'Email already exists'},status= status.HTTP_400_BAD_REQUEST)
             
        if EmailOTP.objects.filter(email=email).exists():
            otp_obj = EmailOTP.objects.get(email=email)

            if otp_obj.otp_created_at + timedelta(minutes=5) < timezone.now() or otp_obj.otp != email_otp:
                raise serializers.ValidationError({"error":"Verification failed"}, status= status.HTTP_401_UNAUTHORIZED)
               
            else:
                otp_obj.delete()
                return attrs
      
    def create(self, validated_data):
        user = User.objects.create_user(email=validated_data['email'], 
                                        password=validated_data['password'])
        user.save()
        return {
            "message": "User Created Successfully",
            "tokens" : user.get_tokens
        }
        

          
class LoginSerializer(serializers.Serializer):
    
    message= serializers.CharField(read_only=True)
    email = serializers.EmailField(max_length=255, write_only=True)
    password = serializers.CharField(write_only=True, min_length=8)
    tokens = serializers.JSONField(read_only=True)
    
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        email = normalize_email(email)
        try:
            user = User.objects.get(email__iexact = email)
        except:

            raise serializers.ValidationError({"error":"Invalid user"}, status=status.HTTP_404_NOT_FOUND)
      
        user = authenticate(
            email=email,
            password=password
        )
        
        if not user:
            raise serializers.ValidationError({"error":"Incorrect Credentials"}, status=status.HTTP_404_NOT_FOUND)

        return {
            'message': "Login Successful",
            'tokens': user.get_tokens,
        }
 
class SendOTPSerializer(serializers.Serializer):
    
    email = serializers.EmailField(write_only=True)
    def create(self, validated_data):
        email = validated_data['email']
        email = normalize_email(email)
       
        if EmailOTP.objects.filter(email__iexact=email).exists():
            otp_object = EmailOTP.objects.get(email__iexact=email)
            
            if otp_object.otp_created_at + timedelta(minutes=1) >= timezone.now():
               raise serializers.ValidationError(status=status.HTTP_408_REQUEST_TIMEOUT)
        
        try:
            print(1223)
            otp = random.randint(1000, 9999)
            send_otp_via_mail(email, otp)
            print('ijjjj')
            EmailOTP.objects.update_or_create(email=email,default= {'otp':otp})
            print("idk")
            return {
                'message': "OTP has been sent."
            }
    
        except:
            raise serializers.ValidationError({"message":"Can't send email"})
            
            
class VerifyotpSerializer(serializers.Serializer):
    
    email= serializers.EmailField(write_only=True)
    otp = serializers.IntegerField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        otp = attrs.get('otp')
        email = normalize_email(email)
        if EmailOTP.objects.filter(email=email).exists():
            otp_obj = EmailOTP.objects.get(email=email)
            if otp_obj.otp_created_at + timedelta(minutes=5) >= timezone.now():
                if otp_obj.otp != otp :
                    raise serializers.ValidationError({"error":"wrong otp"}, status=status.HTTP_401_UNAUTHORIZED)
                else:
                   otp_obj.delete()
                   return{
                        "message": "OTP has been verified Successfully"
                    }
            else:
               raise serializers.ValidationError({"error":"OTP TIMEOUT"},status=status.HTTP_408_REQUEST_TIMEOUT)
                
         
 