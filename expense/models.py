from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from Authentication.models import User
from django.utils import timezone
from datetime import date, time, datetime
# Create your models here.

class Category(models.Model):
     user = models.ForeignKey(User, on_delete=models.CASCADE)
     name = models.CharField(max_length=50)

     def __str__(self):
        return self.name

class expenses(models.Model):
    amount = models.DecimalField(blank=False, decimal_places=2 , max_digits= 9, validators=[MinValueValidator(Decimal("1.00"))] )
    note= models.CharField(max_length=100 ,null=True, blank=True)
    date= models.DateField(default=date.today)
    time= models.TimeField(default=datetime.now().time())
    category = models.CharField(blank=False, max_length=50)

    user = models.ForeignKey(User, on_delete= models.CASCADE)
    image = models.FileField(null=True, blank=True, upload_to ='upload_pics/')
    is_credit= models.BooleanField(default=False)

    def __str__(self):
        return f"{self.amount}"

   
class Budget(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    need = models.IntegerField( default=0)
    luxury = models.IntegerField( default=0)
    savings = models.IntegerField( default=0)

    def __str__(self):
        return f"{self.user.email}"