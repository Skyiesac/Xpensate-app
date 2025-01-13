from import_export import fields, resources
from .models import expenses
from datetime import datetime


class ExpensesResource(resources.ModelResource):
    class Meta:
        model = expenses
        field = ["category", "amount", "is_credit", "date", "time"]
        exclude = ["id", "user", "image"]
