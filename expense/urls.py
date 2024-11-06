from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView

urlpatterns = [
    path('create/', views.CreatexpView.as_view()),
    path('category/', views.CategorylistView.as_view()),
   ]
