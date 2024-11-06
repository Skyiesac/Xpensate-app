from rest_framework import serializers, status
from rest_framework.generics import *
from .serializers import *
from .models import *
from rest_framework.permissions import IsAuthenticated ,AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone 
from datetime import datetime
import re

# change permission class in end

class CategorylistView(APIView):
    permission_classes=[IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        default_cat = ['Food', 'Bills','Shopping','Groceries', 'Fare','Travel']
        default_cats = [Category(name=cat) for cat in default_cat]
        
        user_categories = Category.objects.filter(user=request.user)
        print(user_categories)
        categories= list(default_cats) + list(user_categories)
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)
    
class CreatexpView(CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ExpensesSerializer
  
    def post(self,request, *args, **kwargs):
        data= request.data

        category=data['category']
        if not re.match("^[A-Za-z]+$", category):
           return Response({'error':'Category must contain letters only !'},status=status.HTTP_400_BAD_REQUEST)
        
        if category not in ['Food', 'Bills','Shopping','Groceries', 'Fare','Travel']:
          if not Category.objects.filter(name=category, user=request.user).exists():
            cat= Category.objects.create(
               user=request.user,
               name=category, 
             )
            cat.save()
            print("saved")
            
        serializer = ExpensesSerializer(data= request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_204_NO_CONTENT)

