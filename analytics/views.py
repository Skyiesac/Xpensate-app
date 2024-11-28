from rest_framework import serializers, status
from rest_framework.generics import *
from rest_framework.permissions import IsAuthenticated ,AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
import requests
import json
from decouple import config
from paypal.standard.forms import PayPalPaymentsForm
from django.conf import settings
from django.http import JsonResponse
from .paypal import *
import uuid
from django.urls import reverse
    
class CurrencyConverterView(APIView):
      def get(self, request, *args, **kwargs):
        api_key=config('CURRENCY_API')
        currency_url= f"https://v6.exchangerate-api.com/v6/{api_key}/codes"

        currency_request= requests.get(currency_url).json()

        supported_codes= currency_request.get('supported_codes',[])
       
        return Response({
            "success":True,
            "data": supported_codes
        }, status=status.HTTP_200_OK)


      def post(self, request, *args, **kwargs):
        from_currency= request.data['from_currency']
        to_currency= request.data['to_currency']
        money= request.data['money']
        api_key=config('CURRENCY_API')
        
        if not all([from_currency, to_currency, money]):
            return Response({
                "success": False,
                "error": "Invalid input parameters"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        currency_url= f"https://v6.exchangerate-api.com/v6/{api_key}/pair/{from_currency}/{to_currency}/{money}"
        currency_request= requests.get(currency_url)
        response= currency_request.json()
        result=response['conversion_result']
        return Response({
            "success":True,
            "value":result
        }, status=status.HTTP_200_OK)


class Checkout(APIView):
   
   def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            sender_email = data["sender_email"]
            receiver_email = data["receiver_email"]
            amount = data["amount"]

            response = create_payout(sender_email, receiver_email, amount)

            if response["status"] == "SUCCESS":
                return JsonResponse({"message": "Payment sent successfully", "payout_batch_id": response["payout_batch_id"]})
            else:
                return JsonResponse({"message": "Payment failed", "error": response["error"]}, status=status.HTTP_400_BAD_REQUEST)

        except KeyError as e:
            return JsonResponse({"message": f"Missing field: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return JsonResponse({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
