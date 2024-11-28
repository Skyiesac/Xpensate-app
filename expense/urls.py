from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView

urlpatterns = [
    path('create/', views.CreatexpView.as_view()),
    path('category/', views.CategorylistView.as_view()),
    path('update/<int:id>/', views.UpdateexpView.as_view()),
    path('list/', views.ListExpensesView.as_view()),
    path('category-expense/', views.CategoryexpView.as_view()),
    path('days-expense/', views.DaybasedexpView.as_view()),
   path('create-budget/', views.CreateBudgetView.as_view(),),
   path('monthly-limit/', views.UsermonthlyView.as_view(),),
   path('last-fourexp/', views.LastFourExpensesView.as_view()),
   path('userbudget/', views.ListBudgetsView.as_view()),
   
   ]
