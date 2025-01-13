from rest_framework import serializers, status
from rest_framework.generics import *
from .serializers import *
from .models import *
from django.db.models import Sum, Case, When, F
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from datetime import datetime
import re
from django.utils.dateparse import parse_date
from django.db.models import Value, DecimalField
from django.db.models.functions import Coalesce
from .resources import *
from django.http import HttpResponse

# change permission class in end


class CategorylistView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        default_cat = [
            "Food and Drinks",
            "Shopping",
            "Housing",
            "Transportation",
            "Life and Entertainment",
            "Technical Appliance",
            "Income",
            "Investment",
            "Others",
        ]
        default_cats = [Category(name=cat) for cat in default_cat]

        user_categories = Category.objects.filter(user=request.user)
        categories = list(default_cats) + list(user_categories)
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)


class CreatexpView(CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ExpensesSerializer

    def post(self, request, *args, **kwargs):
        data = request.data
        try:
            category = data["category"]
        except:
            return Response(
                {"success": "False", "error": "Category not found"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not re.match(r"^[A-Za-z\s]+$", category):
            return Response(
                {"success": "False", "error": "Category must contain letters only !"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        category = category.lower().capitalize()
        if category not in [
            "Food and Drinks",
            "Shopping",
            "Housing",
            "Transportation",
            "Life and Entertainment",
            "Technical Appliance",
            "Income",
            "Investment",
            "Others",
        ]:
            if not Category.objects.filter(name=category, user=request.user).exists():
                Category.objects.create(
                    user=request.user,
                    name=category,
                )

        data = request.data.copy()
        # Make a mutable copy of the QueryDict to resolve immutable error
        data["category"] = data["category"].lower().capitalize()

        serializer = ExpensesSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save(user=request.user)

            return Response(
                {"success": "True", "message": "Expense added successfully!"},
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {"success": "False", "error": "Data is not correct"},
            status=status.HTTP_204_NO_CONTENT,
        )


class UpdateexpView(UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ExpensesSerializer

    def get(self, request, id):
        if expenses.objects.filter(id=id, user=request.user).exists():
            expense = expenses.objects.get(id=id, user=request.user)
            serializer = ExpensesSerializer(expense)
            return Response(serializer.data)
        return Response(
            {"success": "False", "message": "This expense doesn't exist."},
            status=status.HTTP_404_NOT_FOUND,
        )

    def post(self, request, id, *args, **kwargs):
        try:
            expense = expenses.objects.get(id=id, user=request.user)
        except:
            return Response(
                {"success": "False", "error": "This expense doesn't exist."},
                status=status.HTTP_404_NOT_FOUND,
            )
        data = request.data
        try:
            category = data["category"]
        except:
            return Response(
                {"success": "False", "error": "Category not found"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not re.match(r"^[A-Za-z\s]+$", category):
            return Response(
                {"success": "False", "error": "Category must contain letters only !"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        category = category.lower().capitalize()
        if category not in [
            "Food and Drinks",
            "Shopping",
            "Housing",
            "Transportation",
            "Life and Entertainment",
            "Technical Appliance",
            "Income",
            "Investment",
            "Others",
        ]:
            if not Category.objects.filter(name=category, user=request.user).exists():
                cat = Category.objects.create(
                    user=request.user,
                    name=category,
                )

        data = request.data.copy()
        # Make a mutable copy of the QueryDict
        data["category"] = data["category"].lower().capitalize()

        serializer = ExpensesSerializer(expense, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"success": "True", "message": "Expense updated successfully!"},
                status=status.HTTP_200_OK,
            )
        return Response(
            {"success": "False", "error": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def delete(self, request, id, *args, **kwargs):
        try:
            expense = expenses.objects.get(id=id, user=request.user)
            expense.delete()
            return Response(
                {"success": "True", "message": "Expense deleted successfully"},
                status=status.HTTP_200_OK,
            )
        except:
            return Response(
                {"success": "False", "message": "This expense doesn't exist."},
                status=status.HTTP_404_NOT_FOUND,
            )


class ListExpensesView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ExpensesSerializer

    def get(self, request, *args, **kwargs):
        expense = expenses.objects.filter(user=request.user)

        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")

        if start_date and end_date:
            expense = expense.filter(date__range=[start_date, end_date])

        if expense is None:
            return Response(
                {"success": "False", "message": "No expenses found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        else:
            exp = expense
            total_expenses = exp.aggregate(
                total=Coalesce(
                    Sum(
                        Case(
                            When(is_credit=True, then=-F("amount")),
                            When(is_credit=False, then=F("amount")),
                            default=Value(0),
                            output_field=DecimalField(),
                        )
                    ),
                    Value(0, output_field=DecimalField()),
                )
            )["total"]

            expenses_list = expense.order_by("-date", "-time")
            serializer = ExpensesSerializer(expenses_list, many=True)

            return Response(
                {"total_expense": total_expenses, "expenses": serializer.data},
                status=status.HTTP_200_OK,
            )


class CategoryexpView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        expense = expenses.objects.filter(user=request.user)
        now = timezone.now()
        exp = expense.filter(date__year=now.year, date__month=now.month)

        total_expenses = exp.aggregate(
            total=Coalesce(
                Sum(
                    Case(
                        When(is_credit=True, then=0),
                        When(is_credit=False, then=F("amount")),
                        default=Value(0),
                        output_field=DecimalField(),
                    )
                ),
                Value(0, output_field=DecimalField()),
            )
        )["total"]

        expense_by_category = (
            expense.values("category")
            .annotate(
                total=Coalesce(
                    Sum(
                        Case(
                            When(is_credit=True, then=0),
                            When(is_credit=False, then=F("amount")),
                            default=Value(0),
                            output_field=DecimalField(),
                        )
                    ),
                    Value(0, output_field=DecimalField()),
                )
            )
            .order_by("category")
        )

        # expense_by_category_dict = {item['category']: item['category_total'] for item in expense_by_category}
        expense_by_category_list = list(expense_by_category)
        if expense_by_category_list:
            return Response(
                {
                    "total_expenses": total_expenses,
                    "expenses_by_category": expense_by_category_list,
                },
                status=status.HTTP_200_OK,
            )

        else:
            return Response(
                {
                    "success": "False",
                    "error": "This list is either empty or Unable to load the required list",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


class DaybasedexpView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        expense = expenses.objects.filter(user=request.user)
        now = timezone.now()
        exp = expense.filter(date__year=now.year, date__month=now.month)
        total_expenses = exp.aggregate(
            total=Coalesce(
                Sum(
                    Case(
                        When(is_credit=True, then=-F("amount")),
                        When(is_credit=False, then=F("amount")),
                        default=Value(0),
                        output_field=DecimalField(),
                    )
                ),
                Value(0, output_field=DecimalField()),
            )
        )["total"]
        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")

        if start_date and end_date:
            start_date = parse_date(start_date)
            end_date = parse_date(end_date)
            expense = expense.filter(date__range=[start_date, end_date])

        expense_by_days = (
            expense.values("date")
            .annotate(
                total=Coalesce(
                    Sum(
                        Case(
                            When(is_credit=True, then=-F("amount")),
                            When(is_credit=False, then=F("amount")),
                            default=Value(0),
                            output_field=DecimalField(),
                        )
                    ),
                    Value(0, output_field=DecimalField()),
                )
            )
            .order_by("-date")
        )

        expenses_by_day_list = list(expense_by_days)
        if expenses_by_day_list:
            return Response(
                {
                    "total_expenses": total_expenses,
                    "expenses_by_day": expenses_by_day_list,
                }
            )
        else:
            return Response(
                {
                    "success": "False",
                    "error": "This list is either empty or unable to load the required list",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


class Expenseexport(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")

        if start_date and end_date:
            start_date = parse_date(start_date)
            end_date = parse_date(end_date)
            expense = expenses.objects.filter(
                user=request.user, date__range=[start_date, end_date]
            )
        else:
            expense = expenses.objects.filter(user=request.user)

        expense_resource = ExpensesResource().export(expense)
        response = HttpResponse(expense_resource.csv, content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="expenses.csv"'
        return response


class CreateBudgetView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        try:
            budget = Budget.objects.get(user=user)
            serializer = BudgetSerializer(
                budget, data=request.data, context={"request": request}
            )
        except Budget.DoesNotExist:
            serializer = BudgetSerializer(
                data=request.data, context={"request": request}
            )

        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "success": "True",
                    "message": "Budget created or updated successfully!",
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {"success": "False", "error": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )


class ListBudgetsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        budget = Budget.objects.get(user=request.user)
        serializer = BudgetSerializer(budget)
        return Response(
            {
                "success": True,
                "monthly": request.user.monthlylimit,
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class UsermonthlyView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            limit = request.data["monthlylimit"]
        except:
            return Response(
                {"success": "False", "error": "Value is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if limit is None:
            return Response(
                {"success": "False", "error": "Name is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user = request.user
        user.monthlylimit = limit
        user.save()

        return Response(
            {"success": "True", "message": "Monthly limit updated successfully."},
            status=status.HTTP_200_OK,
        )


class LastFourExpensesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        last_four_expenses = expenses.objects.filter(user=user).order_by(
            "-date", "-time"
        )[:4]
        serializer = ExpensesSerializer(last_four_expenses, many=True)
        return Response(
            {"success": True, "data": serializer.data}, status=status.HTTP_200_OK
        )


class BudgetFullView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):

        current_date = timezone.now()
        current_month = current_date.month
        current_year = current_date.year

        NEEDS_CATEGORIES = [
            "Food and Drinks",
            "Housing",
            "Transportation",
            "Life & Entertainment",
        ]
        LUXURY_CATEGORIES = [
            "Shopping",
            "Technical Appliance",
            "Income",
            "Investment",
            "Others",
        ]
        needs_debit_total = (
            expenses.objects.filter(
                user=request.user,
                category__in=NEEDS_CATEGORIES,
                date__year=current_year,
                date__month=current_month,
                is_credit=False,
            ).aggregate(total=Sum("amount"))["total"]
            or 0
        )

        luxury_debit_total = (
            expenses.objects.filter(
                user=request.user,
                category__in=LUXURY_CATEGORIES,
                date__year=current_year,
                date__month=current_month,
                is_credit=False,
            ).aggregate(total=Sum("amount"))["total"]
            or 0
        )

        needs_credit_total = (
            expenses.objects.filter(
                user=request.user,
                category__in=NEEDS_CATEGORIES,
                date__year=current_year,
                date__month=current_month,
                is_credit=True,
            ).aggregate(total=Sum("amount"))["total"]
            or 0
        )

        luxury_credit_total = (
            expenses.objects.filter(
                user=request.user,
                category__in=LUXURY_CATEGORIES,
                date__year=current_year,
                date__month=current_month,
                is_credit=True,
            ).aggregate(total=Sum("amount"))["total"]
            or 0
        )

        return Response(
            {
                "success": True,
                "monthly": request.user.monthlylimit,
                "needs_debit_total": needs_debit_total,
                "luxury_debit_total": luxury_debit_total,
                "needs_credit_total": needs_credit_total,
                "luxury_credit_total": luxury_credit_total,
            },
            status=status.HTTP_200_OK,
        )


class IncomexpenseView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        now = timezone.now()
        current_year = now.year
        current_month = now.month

        monthly_expenses = expenses.objects.filter(
            user=user, date__year=current_year, date__month=current_month
        )
        total_income = (
            monthly_expenses.filter(is_credit=True).aggregate(total=Sum("amount"))[
                "total"
            ]
            or 0
        )
        total_expense = (
            monthly_expenses.filter(is_credit=False).aggregate(total=Sum("amount"))[
                "total"
            ]
            or 0
        )

        return Response(
            {
                "success": True,
                "total_income": total_income,
                "total_expense": total_expense,
            },
            status=status.HTTP_200_OK,
        )
