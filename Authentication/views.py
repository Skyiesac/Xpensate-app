from rest_framework import serializers, status
from rest_framework.generics import *
from Authentication.serializers import *
from rest_framework.permissions import AllowAny, IsAuthenticated 
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import *
from .utils import send_otpphone
import json 
from decouple import config
import requests

class RegisterAPIView(CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class= RegisterSerializer
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        user = serializer.save()
        return Response({"message": "Verify OTP to register successfully!"}, status=status.HTTP_201_CREATED)
    
class LoginAPIView(APIView):
   permission_classes = [AllowAny]
 
   def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data = request.data)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.validated_data, status=status.HTTP_200_OK)

class VerifyOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        print("Request Data:", request.data) 
        serializer = VerifyOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class ForgetPassword(APIView):
    permission_classes = [AllowAny]
    def post(self, request, *args, **kwargs):
        serializer = ForgetPassSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({'message':'OTP sent on mail'}, status=status.HTTP_200_OK)


class ForgetOTPverView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = verifyforgetserializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'message':'OTP Verified successfully!'}, status=status.HTTP_200_OK)


class ResetPassView(UpdateAPIView):
    permission_classes = [AllowAny]
    serializer_class = ResetPassSerializer
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'messsage':['Password changed successfully']}, status=status.HTTP_200_OK)


class Sendotpphone(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
       contact = request.data['contact']
       if contact is None:
              return Response({ 'success':'False',
                  'message':'Contact is required'}, status=status.HTTP_400_BAD_REQUEST)
       
       if User.objects.filter(contact=contact).exists():
           return Response({ 'success':'False',
               'message':'Contact already exists'}, status=status.HTTP_400_BAD_REQUEST)
       
       otp = send_otpphone(contact)
       PhoneOTP.objects.update_or_create(contact=contact, 
                                         defaults={"otp" : otp})
       return Response({ 'success':'True',
           'message':'OTP sent successfully!'}, status=status.HTTP_200_OK)

class VerifyPhoneOTP(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        contact= str(request.data['contact'])
        otp = int(request.data.get('otp'))
        if request.data['contact'] is None:
              return Response({ 'success':'False',
                  'message':'Contact is required'}, status=status.HTTP_400_BAD_REQUEST)
       
        if request.data['otp'] is None:
              return Response({ 'success':'False',
                  'message':'OTP is required to verify'}, status=status.HTTP_400_BAD_REQUEST)
       
        try:
          userotp= PhoneOTP.objects.get(contact= contact)
        except:  
          return Response({ "success":"False",
                           "error": "This OTP is not valid"}, status=status.HTTP_400_BAD_REQUEST)
        otph = userotp.otp
        if otph != otp:
                return Response({'success':'False',
                    'error':'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)
        if userotp.otp_created_at + timedelta(minutes=5)< timezone.now() :
                return Response({'success':'False',
                    'error':'OTP expired, Resend OTP'}, status=status.HTTP_400_BAD_REQUEST)
        
        user = request.user
        user.contact=contact
        user.save()
        PhoneOTP.objects.get(contact=contact).delete()
           
        return Response({'success':'True',
            'message':'Phone number verified successfully!'}, status=status.HTTP_200_OK)     
    
class UpdateUsernameView(APIView):
    permission_classes= [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        name= request.data['name']
        if name is None:
            return Response({
                "success":"False",
                "error":"Name is required"
            }, status=status.HTTP_400_BAD_REQUEST)
        user= request.user
        user.name= name
        user.save()

        return Response({
            "success":"True",
            "message":"Name updated successfully."
        }, status=status.HTTP_200_OK)
    
class UpdatecurrencyView(APIView):
    permission_classes=[IsAuthenticated]

    def post(self, request, *args, **kwargs):
        currency= request.data['currency']
        if len(currency)>3:
            return Response({
                "success":"False",
                "error":"Write a valid code"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        user= request.user
        user.currency= currency
        user.save()

        api_key=config('CURRENCY_API')
        curr_url= f"https://v6.exchangerate-api.com/v6/{api_key}/pair/INR/{currency}"
        currency_request= requests.get(curr_url).json()
        user.currency_rate= currency_request['conversion_rate']
        result= currency_request['conversion_rate']
        return Response({
            "success":"True",
            "message":"Currency preference updated successfully.",
            # "value":result,
        }, status=status.HTTP_200_OK)
