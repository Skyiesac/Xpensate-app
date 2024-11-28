from django.urls import path , include
from .views import *

urlpatterns = [
    path('create/', CreateGroupView.as_view()),
    path('joingroup/', JoinwcodeView.as_view()),
    path('add-remove/<int:id>/<str:email>/', AddRemovememView.as_view()),
    path('addexp/<int:id>/', CreateexpView.as_view()),
    path('editexp/<int:id>/', EditExpView.as_view()),
    path('deletexp/', DeleteexpView.as_view()),
    path('tripgroup/<int:id>/', GroupDetailsView.as_view()),
    path('tosettle/', SettlementView.as_view()),
    path('usergroups/',UserTripGroupsView.as_view()),
    path('groupdetail/<int:id>/',GroupMembersView.as_view()),
    #debts
    path('createdebt/', CreateDebtView.as_view()),
    path('debts/', DebtListView.as_view()),
    path('markdebtpaid/', MarkDebtAsPaidView.as_view()),
]
