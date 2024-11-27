from rest_framework import serializers
from .models import Category, expenses, Budget
from Authentication.models import User

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['name',]

class ExpensesSerializer(serializers.ModelSerializer):
    class Meta:
        model = expenses
        fields = ['id','amount', 'note','date','time','category', 'image', 'is_credit']
    
    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user
        currency_rate = user.currency_rate 

        validated_data['amount'] = validated_data['amount'] / currency_rate

        return super().create(validated_data)
    

class BudgetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Budget
        fields = ['user', 'need', 'luxury', 'savings']
       