
from django.urls import path
from .views import *
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView

urlpatterns = [
    path("generate/token/", TokenObtainPairView.as_view()),
    path("verify/", TokenVerifyView.as_view()),
    path("refresh/", TokenRefreshView.as_view()),
    path('register/', RegisterAPIView.as_view()),
    path('verifyregister/', VerifyRegisterView.as_view()),
    path('login/', LoginAPIView.as_view()),
    # path('otpsend/', SendOTP.as_view()),
    # path('otpverify/', VerifyOTP.as_view()),
  #   path('passforget/', ForgetPassword.as_view()),
   
]
