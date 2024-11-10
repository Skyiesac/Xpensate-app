from rest_framework import serializers, status
from rest_framework.generics import *
from expense.models import *
from rest_framework.permissions import IsAuthenticated ,AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
import matplotlib.pyplot as plt
import io
import base64
from scipy.interpolate import make_interp_spline
import numpy as np
import matplotlib.dates as mdates
# Create your views here.
   
class DaybasedGraphView(APIView):
        permission_classes = [IsAuthenticated]
    
        def get(self, request, *args, **kwargs):
            expense = expenses.objects.filter(user=request.user)
            
            start_date = request.query_params.get('start_date')
            end_date = request.query_params.get('end_date')
            if start_date:
             try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                expense = expense.filter(date__gte=start_date)
             except ValueError:
                return Response({ "success":"False",
                   "error": "Invalid start_date format. Please use YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)
            if end_date:
              try:
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
                expense = expense.filter(date__lte=end_date)
              except ValueError:
                return Response({"success":"False",
                   "error": "Invalid end_date format. Please use YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)

            expense = expense.order_by('date')
            expenses_by_day = {}
            total_expenses = 0

            for exp in expense:
                if exp.is_credit:
                 amount = -exp.amount
                else:
                 amount=exp.amount
                total_expenses += amount
    
                if exp.date not in expenses_by_day:
                    expenses_by_day[exp.date] = 0
                expenses_by_day[exp.date] += amount
    
            dates = list(expenses_by_day.keys())
            totals = list(expenses_by_day.values())
            plt.figure(figsize=(10, 5))  # in inches

            if len(dates) >=4:
                date_strs = [date.strftime('%Y-%m-%d') for date in dates]
            
                # Convert dates to numerical format
                date_num = np.arange(len(dates))
                #spline to add curve 
                spline = make_interp_spline(date_num, totals, k=3)
                date_smooth = np.linspace(date_num.min(), date_num.max(), 300)
                total_smooth = spline(date_smooth)

                plt.plot(date_smooth, total_smooth, color='green')
                plt.xticks(date_num, date_strs, rotation=45)
            else:
                plt.plot(dates, totals, marker='o', color='green')
                

            plt.title('Expenses graph')
            plt.xlabel('Date')
            plt.ylabel('Total Expense')
            plt.grid(False)

            buf = io.BytesIO()
            plt.savefig(buf, format='png')
            buf.seek(0)
            plt.close()

            # Encode the image to base64
            image_final = base64.b64encode(buf.read()).decode('utf-8')
            image_data = base64.b64decode(image_final)

            # Save the image to a file
            with open("expense_graph.png", "wb") as f:
                f.write(image_data)

            print("Image saved as expense_graph.png")
            return Response({
               "success":"True",
               "total": total_expenses,
                "graph": image_final
            },status=status.HTTP_200_OK)
    
    