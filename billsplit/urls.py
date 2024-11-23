
from django.urls import path
from .views import *
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView

urlpatterns = [
     path('groups/',AllGroupsView.as_view()),
     path('addgroup/', AddGroupView.as_view()),
     path('add/members/', AddMemberView.as_view()), #group id
     path('remove/members/<int:id>/', RemovememberView.as_view()), #group id
     path('createbill/', CreateBillView.as_view()), #group id
     path('markpaid/<int:id>/', MarkAsPaidView.as_view()),  #bill id
     path('recentsplits/', RecentsplitsView.as_view()),  #bill id
     
     path('groupdetail/<int:id>/', GroupDetailView.as_view()),  #bill id
      
     
]
