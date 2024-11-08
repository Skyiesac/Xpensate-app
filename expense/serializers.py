from rest_framework import serializers
from .models import Category, expenses


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['name',]

class ExpensesSerializer(serializers.ModelSerializer):
    class Meta:
        model = expenses
        fields = ['amount', 'note','date','time','category', 'image']
   