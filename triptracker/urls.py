from django.urls import path , include
from .views import *

urlpatterns = [
    path('create/', CreateGroupView.as_view()),
    path('joingroup/', JoinwcodeView.as_view()),
    path('add/<int:id>/', AddRemovememView.as_view()),
    path('addexp/<int:id>/', CreateexpView.as_view()),
    path('editexp/<int:id>/', EditExpView.as_view()),
    path('deletexp/', DeleteexpView.as_view()),
]
