
from django.urls import path
from .views import *
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView

urlpatterns = [
     path('groups/', DashboardView.as_view()),
     path('addgroup/', AddGroupView.as_view()),
     path('add-remove/members/<int:id>/', AddRemoveMemberView.as_view()), #group id
     path('createbill/', CreateBillView.as_view()), #group id
     path('markpaid/<int:id>/', MarkAsPaidView.as_view()),  #bill id
     path('recentsplits/', Recentsplits.as_view()),  #bill id
     
   
     
]
