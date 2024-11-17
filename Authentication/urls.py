
from django.urls import path
from .views import *
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView

urlpatterns = [
    path("generate/token/", TokenObtainPairView.as_view()),
    path("verify/", TokenVerifyView.as_view()),
    path("refresh/", TokenRefreshView.as_view()),
    path('register/', RegisterAPIView.as_view()),
    path('verifyotp/', VerifyOTPView.as_view()),
    path('login/', LoginAPIView.as_view()),
   
   path('passforget/', ForgetPassword.as_view()),
   path('pass/otpverify/', ForgetOTPverView.as_view()),
   path('passreset/', ResetPassView.as_view()),
   path('phoneverify/', Sendotpphone.as_view()),
   path('phone/otpverify/', VerifyPhoneOTP.as_view()),
   
]
