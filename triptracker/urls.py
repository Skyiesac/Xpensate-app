from django.urls import path , include
from .views import *

urlpatterns = [
    path('create/', createGroupView.as_view()),
    path('joingroup/', JoinwcodeView.as_view()),
    path('add/<int:id>/', AddRemovememView.as_view()),
]
