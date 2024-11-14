
from django.urls import path
from .views import *
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView

urlpatterns = [
     path('create/', DashboardView.as_view()),
     path('addgroup/', AddGroupView.as_view()),
     path('add-remove/members/<int:id>/', AddRemoveMemberView.as_view()),
     path('create_bill/<int:id>', CreateBillView.as_view(), name='create-bill'),

     # path('memexpenses/', GroupMemberExpensesView.as_view(), name='group-member-expenses'),

   
     
]
