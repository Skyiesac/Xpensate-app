from django.urls import path
from . import views

urlpatterns = [
    path('linegraph/', views.DaybasedGraphView.as_view()),
     # request format GET /graph/?start_date=2024-11-01&end_date=2024-11-10
    path('convert-currency/',views.CurrencyConverterView.as_view())
    ]
