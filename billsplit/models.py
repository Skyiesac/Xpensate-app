from django.db import models
from Authentication.models import User
# Create your models here.

class Group(models.Model):
    name = models.CharField(max_length=50)
    members = models.ManyToManyField(User, through="GroupMember")
    groupowner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='admin',to_field='email')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class GroupMember(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    member = models.ForeignKey(User, on_delete=models.CASCADE, to_field='email')
    date_join = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('member', 'group')

    def __str__(self):
        return f"{self.group} - {self.member}"
     
class Bill(models.Model):
    billowner = models.ForeignKey(User, on_delete=models.CASCADE , related_name='owned_bills', to_field='email')
    bill_participants = models.ManyToManyField(User, through="BillParticipant", related_name='participated_in_bills')
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    billname = models.CharField(null=True, max_length=20)
    billdate = models.DateTimeField(null=True, auto_now_add=True)
    
    def __str__(self):
        return self.billname  if self.billname else "Unnamed Bill"


class BillParticipant(models.Model):
    bill = models.ForeignKey(Bill, on_delete=models.CASCADE)
    participant = models.ForeignKey(User, on_delete=models.CASCADE,  to_field='email')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid = models.BooleanField(default=False)
    
    def __str__(self):
        return  self.participant.email
 