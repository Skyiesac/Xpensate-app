from django.urls import path
from . import views
from django.urls import path, include

urlpatterns = [
    path("convert-currency/", views.CurrencyConverterView.as_view()),
]
