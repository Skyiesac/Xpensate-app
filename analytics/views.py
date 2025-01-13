from rest_framework import status
from rest_framework.generics import *
from rest_framework.response import Response
from rest_framework.views import APIView
import requests
from decouple import config
from django.urls import reverse


class CurrencyConverterView(APIView):
    def get(self, request, *args, **kwargs):
        api_key = config("CURRENCY_API")
        currency_url = f"https://v6.exchangerate-api.com/v6/{api_key}/codes"

        currency_request = requests.get(currency_url).json()

        supported_codes = currency_request.get("supported_codes", [])

        return Response(
            {"success": True, "data": supported_codes}, status=status.HTTP_200_OK
        )

    def post(self, request, *args, **kwargs):
        try:
            from_currency = request.data["from_currency"]
            to_currency = request.data["to_currency"]
            money = request.data["money"]
        except:
            return Response(
                {"success": False, "error": "Data is missing!!"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        api_key = config("CURRENCY_API")

        if not all([from_currency, to_currency, money]):
            return Response(
                {"success": False, "error": "Invalid input parameters"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        currency_url = f"https://v6.exchangerate-api.com/v6/{api_key}/pair/{from_currency}/{to_currency}/{money}"
        currency_request = requests.get(currency_url)
        response = currency_request.json()
        result = response["conversion_result"]
        return Response({"success": True, "value": result}, status=status.HTTP_200_OK)
