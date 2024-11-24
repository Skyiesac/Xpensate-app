from django.urls import path , include
from .views import *

urlpatterns = [
    path('create/', CreateGroupView.as_view()),
    path('joingroup/', JoinwcodeView.as_view()),
    path('add/<int:id>/', AddRemovememView.as_view()),
    path('addexp/<int:id>/', CreateexpView.as_view()),
    path('editexp/<int:id>/', EditExpView.as_view()),
    path('deletexp/', DeleteexpView.as_view()),
    path('tripgroup/<int:id>/', GroupDetailsView.as_view()),
    path('tosettle/<int:id>/', GroupSettlementsView.as_view()),
    path('createdebt/', CreateDebtView.as_view()),
    path('debts/', DebtListView.as_view()),
    path('markdebtpaid/', MarkDebtAsPaidView.as_view()),
]
