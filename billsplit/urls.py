
from django.urls import path
from .views import *
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView

urlpatterns = [
     path('create/', DashboardView.as_view()),
     path('addgroup/', AddGroupView.as_view()),
     path('group/<int:id>/', AddGroupMemberView.as_view()),

]
