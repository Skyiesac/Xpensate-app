from django.db import models
from Authentication.models import User
from django.core.validators import MinValueValidator
from .utils import generate_invite_code
from decimal import Decimal
# Create your models here.

class Tripgroup(models.Model):
    name = models.CharField(max_length=50)
    members = models.ManyToManyField(User, through="TripMember")
    invitecode= models.CharField(max_length=8, unique=True, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.invitecode:
            self.invitecode = generate_invite_code()
        super().save(*args, **kwargs)

class TripMember(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(Tripgroup, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'group')

class addedexp(models.Model):
    group = models.ForeignKey(Tripgroup, on_delete=models.CASCADE)
    whatfor= models.CharField(max_length= 20)
    amount= models.DecimalField(max_digits=10, decimal_places=2 , validators=[MinValueValidator(Decimal("1.00"))])
    paidby= models.ForeignKey(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.whatfor
    
class tosettle(models.Model):
     group = models.ForeignKey(Tripgroup, on_delete=models.CASCADE)
     debtamount=models.DecimalField(max_digits=10, decimal_places=2 , validators=[MinValueValidator(Decimal("1.00"))])
     debter=models.ForeignKey(User, on_delete=models.CASCADE ,  related_name='debter_set')   #will pay
     creditor=models.ForeignKey(User, on_delete=models.CASCADE , related_name='creditor_set') #paid alr
     connect = models.ForeignKey(addedexp, on_delete=models.CASCADE, null=True) 

     def __str__(self):
        return f"{self.debter} owes {self.creditor} "