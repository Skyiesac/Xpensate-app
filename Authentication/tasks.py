from celery import shared_task
from django.utils import timezone
from django.utils import timezone
from django.db.models import Sum, Case, When, F, Value, DecimalField
from .models import *
from expense.models import expenses
from .firebase_utils import send_firebase_notification  

def total_expense(user):
    today = timezone.now().date()
    expenses = expenses.objects.filter(user=user, date=today).aggregate(
        total=Sum(
            Case(
                When(is_credit=True, then=-F('amount')),
                When(is_credit=False, then=F('amount')),
                default=Value(0),
                output_field=DecimalField()
            )
        )
    )['total']
    return total_expense or Decimal('0.00')
    

@shared_task
def send_daily_notifications():
    now = timezone.now()
    print("Sending daily notifications")
    tokens= FCMToken.objects.all()
    for tokenuser in tokens:
        total_exp = total_expense(tokenuser.user)
        if(total_exp==0):
            send_firebase_notification(tokenuser.fcm_token, "We missed you today at Xpensate", "You have no expenses today.")
        elif(total_exp>0):
           send_firebase_notification(tokenuser.fcm_token, "Quick reminder from Xpensate", f"Today's expenses totaled- {total_exp}.Keep an eye on your budget.")
        else:
           send_firebase_notification(tokenuser.fcm_token, "Quick reminder from Xpensate", f"Yay! you earned {total_exp} today. Keep up the good work.")