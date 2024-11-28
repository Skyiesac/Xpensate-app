from django.urls import path
from . import views
from django.urls import path , include

urlpatterns = [
    path('linegraph/', views.DaybasedGraphView.as_view()),
     # request format GET /graph/?start_date=2024-11-01&end_date=2024-11-10
    path('convert-currency/',views.CurrencyConverterView.as_view()),
     path('paypal/', include("paypal.standard.ipn.urls")),
    path('payment/', views.Checkout.as_view()),

    ]
