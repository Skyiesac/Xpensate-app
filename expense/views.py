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
        default_cat = ['Food', 'Bills','Shopping','Groceries', 'Fare','Travel','Others']
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
        if not re.match(r"^[A-Za-z\s]+$", category):
           return Response({'error':'Category must contain letters only !'},status=status.HTTP_400_BAD_REQUEST)
        
        category= category.lower().capitalize()
        if category not in ['Food', 'Bills','Shopping','Groceries', 'Fare','Travel','Others']:
          if not Category.objects.filter(name=category, user=request.user).exists():
            Category.objects.create(
               user=request.user,
               name=category, 
             )

 
        data = request.data.copy() 
        # Make a mutable copy of the QueryDict to resolve immutable error      
        data['category'] =  data['category'].lower().capitalize()

        serializer = ExpensesSerializer(data= request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)

            return Response({
               "success":"True",
               "message":"Expense added successfully!"
            }, status=status.HTTP_201_CREATED)
        return Response({
           "success":"False",
           "error": "serializer.error" }, status=status.HTTP_204_NO_CONTENT)

class UpdateexpView(UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ExpensesSerializer
    
    def get(self, request, id):
       if expenses.objects.filter(id=id,user=request.user).exists():
          expense = expenses.objects.get(id=id,user=request.user)
          serializer = ExpensesSerializer(expense)
          return Response(serializer.data)
       return Response({
          "message":"This expense doesn't exist."
       },status=status.HTTP_404_NOT_FOUND)
    
    def put(self, request, id, *args, **kwargs):
        expense= expenses.objects.get(id=id, user=request.user)
        data=request.data

        category=data['category']
        if not re.match(r"^[A-Za-z\s]+$", category):
           return Response({'error':'Category must contain letters only !'},status=status.HTTP_400_BAD_REQUEST)
        
        category= category.lower().capitalize()
        if category not in ['Food', 'Bills','Shopping','Groceries', 'Fare','Travel','Others']:
          if not Category.objects.filter(name=category, user=request.user).exists():
            cat= Category.objects.create(
               user=request.user,
               name=category, 
             )

        data = request.data.copy() 
        # Make a mutable copy of the QueryDict
        data['category'] =  data['category'].lower().capitalize()

        serializer = ExpensesSerializer(expense, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({
             "success":"True",
              "message":"Expense updated successfully!"
            }, status=status.HTTP_200_OK)
        return Response({"success": "False",
          "error":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
       
class DeleteexpView(DestroyAPIView):
    permission_classes= [IsAuthenticated]
    serializer_class = ExpensesSerializer
    
    def get(self, request, id):
       if expenses.objects.filter(id=id,user=request.user).exists():
          expense = expenses.objects.get(id=id,user=request.user)
          serializer = ExpensesSerializer(expense)
          return Response(serializer.data)
       return Response({
          "message":"This expense doesn't exist."
       },status=status.HTTP_404_NOT_FOUND)
    
    def delete(self, request,id, *args, **kwargs):
       expense = expenses.objects.get(id=id, user=request.user)
       expense.delete()
       return Response({"success":"True",
                        'message': 'Expense deleted successfully'},
                    status=status.HTTP_204_NO_CONTENT)

