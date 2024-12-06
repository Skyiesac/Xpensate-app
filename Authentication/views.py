from rest_framework import serializers, status
from rest_framework.generics import *
from Authentication.serializers import *
from rest_framework.permissions import AllowAny, IsAuthenticated 
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import *
from .firebase_utils import *
from .utils import send_otpphone
import json 
from decouple import config
import requests
from .throttle import * 

class RegisterAPIView(CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class= RegisterSerializer
    throttle_classes = [AnonUserRateThrottle]
    
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
    throttle_classes = [AnonUserRateThrottle]

    def post(self, request, *args, **kwargs):
        print("Request Data:", request.data) 
        serializer = VerifyOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class ForgetPassword(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [AnonUserRateThrottle]
    def post(self, request, *args, **kwargs):
        serializer = ForgetPassSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({'message':'OTP sent on mail'}, status=status.HTTP_200_OK)


class ForgetOTPverView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [AnonUserRateThrottle]
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
    throttle_classes = [KnownUserRateThrottle]

    def post(self, request, *args, **kwargs):
       try:
        contact = request.data['contact']
       except:
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
    throttle_classes = [KnownUserRateThrottle]

    def post(self, request, *args, **kwargs):
        contact= str(request.data['contact'])
        otp = int(request.data['otp'])
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
        try:
         name= request.data['name']
        except:
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
        try:
         currency= request.data['currency']
        except:
            return Response({
                "success":"False",
                "error":"Currency is required"
            }, status=status.HTTP_400_BAD_REQUEST)
        if len(currency)>3:
            return Response({
                "success":"False",
                "error":"Write a valid code"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        user= request.user
        user.currency= currency

        api_key=config('CURRENCY_API')
        curr_url= f"https://v6.exchangerate-api.com/v6/{api_key}/pair/INR/{currency}"
        currency_request= requests.get(curr_url).json()
        user.currency_rate= currency_request['conversion_rate']
        user.save()
        result= currency_request['conversion_rate']
        return Response({
            "success":"True",
            "message":"Currency preference updated successfully.",
            # "value":result,
        }, status=status.HTTP_200_OK)
    
class UpdateProfilepicView(APIView):
    permission_classes=[IsAuthenticated]
    
    def patch(self, request, *args, **kwargs):
        user = request.user
        serializer = ProfileImageSerializer(user, data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            return Response({
                "success": "True",
                "message": "Profile image updated successfully."
            }, status=status.HTTP_200_OK)
        
        return Response({
            "success": "False",
            "error": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
class DeviceTokenView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
         fcm_token = request.data['fcm_token']
        except:
            return Response({'error': 'FCM token is not provided.'}, status=status.HTTP_404_NOT_FOUND)

        FCMToken.objects.update_or_create(
            user=request.user,
            defaults={'fcm_token': fcm_token}
        )
        return Response({'message': 'FCM token registered successfully.'})


class TestNotificationView(APIView):
    def post(self, request):
        fcm_token = request.data['fcm_token']
        if not fcm_token:
            return Response({'error': 'FCM token is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            response = send_firebase_notification(
                 )
            return Response({'message': 'Notification sent successfully.', 'response': response})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_502_BAD_GATEWAY)
