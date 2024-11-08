from django.contrib import admin

from django.contrib import admin
from .models import Category, expenses  # Import your models

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'user') 
    search_fields = ('name',)  

class ExpensesAdmin(admin.ModelAdmin):
    list_display = ('amount', 'note', 'date', 'time', 'category', 'user') 
    list_filter = ('date', 'category', 'user')
    search_fields = ('note', 'category') 

admin.site.register(Category, CategoryAdmin)
admin.site.register(expenses, ExpensesAdmin)