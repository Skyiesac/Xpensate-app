from django.shortcuts import render
from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated ,AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import serializers, status
from .serializers import *
from .models import *
from rest_framework.generics import *
from django.db.models import Count, Sum
from .utils import *
from django.db.models import Count, Subquery, OuterRef
from django.utils.dateparse import parse_date
from django.db import transaction
from expense.models import expenses
#To create a group 
class CreateGroupView(APIView):
        permission_classes = [IsAuthenticated]

        def post(self, request, *args, **kwargs):
            if not request.data['name']:
                return Response({ "success" : "False",
                    "error": "Group name cannot be empty"}, status=status.HTTP_400_BAD_REQUEST)
            name = request.data['name']
            serializer= TripgroupSerializer(data=request.data,  context={'request': request})
            if serializer.is_valid():
                group=serializer.save()
                TripMember.objects.create(group=group, user=request.user)
                return Response({
                    "success": "True",
                    "message": "Group created successfully!"
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    "success": "False",
                    "error": serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)

#to join group via invite code
class JoinwcodeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        invitecode = request.data['invitecode']
        if not invitecode:
            return Response({
                "success": "False",
                "error": "Invite code is required"
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            group = Tripgroup.objects.get(invitecode=invitecode)
        except Tripgroup.DoesNotExist:
            return Response({
                "success": "False",
                "error": "Invalid invite code"
            }, status=status.HTTP_400_BAD_REQUEST)

        if TripMember.objects.filter(group=group, user=request.user).exists():
            return Response({
                "success": "False",
                "error":"Already a member of this group"
            }, status=status.HTTP_400_BAD_REQUEST)

        TripMember.objects.create(group=group, user=request.user)
        return Response({
            "success": "True",
            "message": "You have successfully joined the group"
        }, status=status.HTTP_200_OK)

#to add or remove members from the group
class AddRemovememView(APIView):
    permission_classes=[IsAuthenticated]       

    def post(self,request,id,email, *args, **kwargs):
         email=email
         group = Tripgroup.objects.get(id=id)
         if group is None:
                return Response({ "success" : "False",
                    "error": "Group not found"}, status=status.HTTP_400_BAD_REQUEST)
         user = get_object_or_404(User, email=email)

         if TripMember.objects.filter(group=group, user=user).exists():
            return Response({
                "success": "False",
                "error":"Already a member of this group"
            }, status=status.HTTP_400_BAD_REQUEST)
         
         invite_email(email,group.invitecode, group.name)
         return Response({
                "success": "True",
                "message": "Mail sent successfully!"
            }, status=status.HTTP_200_OK)
 
    def delete(self, request, id ,email, *args, **kwargs):
         email=email
         user = get_object_or_404(User, email=email)
         group = Tripgroup.objects.get(id=id)
         if group is None:
                return Response({ "success" : "False",
                    "error": "Group not found"}, status=status.HTTP_400_BAD_REQUEST)
         
            
         if TripMember.objects.filter(group=group, user=user).exists():
            tripmem= TripMember.objects.get(group=group, user=user)
            tripmem.delete()
            return Response({
                "success": "True",
                "error":"Removed a member of this group"
            }, status=status.HTTP_200_OK)
         
         else:
            return Response({
                "success": "False",
                "error":"Not a member of this group"
            }, status=status.HTTP_400_BAD_REQUEST)
            
#to create an expense and create settlements
class CreateexpView(APIView):
    permission_classes=[IsAuthenticated]

    def post(self, request,id, *args , **kwargs):
        group= get_object_or_404(Tripgroup, id=id)
        try:
           trip_mem= TripMember.objects.select_related('user').filter(group=group, user__email=request.data.get('paidby')).first()
        except :
            return Response({
                "success": "False",
                "error": "Email does not exist in the members of this group"
            }, status=status.HTTP_400_BAD_REQUEST)

        user= trip_mem.user
        data = request.data.copy()
        data['group'] = group.id

        serializer = AddedExpSerializer(data=data)
        if serializer.is_valid():
            with transaction.atomic():
                added_exp = serializer.save(paidby=user)
                members = TripMember.objects.filter(group=group)
                memberscnt=members.count()
                debt_amount= added_exp.amount / memberscnt

                for member in members:
                   if member.user != user:
                        tosettle.objects.create(
                            group=group,
                            debter=member.user,
                            creditor=user,
                            debtamount=debt_amount/user.currency_rate,
                            connect=added_exp
                        )

                return Response({
                    "success": "True",
                    "message": "Expense added and settlements created successfully!"
                }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                "success": "False",
                "error": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
#to edit an expense and adjust settlements
class EditExpView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, id, *args, **kwargs):
        group = get_object_or_404(Tripgroup, id=id)
        expense = get_object_or_404(addedexp, id=request.data['expense_id'], group=group)

        try:
            trip_mem = TripMember.objects.get(group=group, user=request.user)
        except :
            return Response({
                "success": "False",
                "error": "You are not a member of this group"
            }, status=status.HTTP_403_FORBIDDEN)

        serializer = AddedExpSerializer(expense, data=request.data)
        if serializer.is_valid():
            with transaction.atomic():
                updated_exp = serializer.save()

                tosettle.objects.filter(connect=expense).delete()
                members = TripMember.objects.filter(group=group)
                members_count = members.count()
                new_debt_amount = updated_exp.amount / members_count

                for member in members:
                        if member.user != updated_exp.paidby:
                            tosettle.objects.create(
                                group=group,
                                debter=member.user,
                                creditor=updated_exp.paidby,
                                debtamount=new_debt_amount/request.user.currency_rate,
                                connect=updated_exp
                            )
           
                return Response({
                    "success": "True",
                    "message": "Expense updated and settlements adjusted successfully!"
                }, status=status.HTTP_200_OK)

        return Response({
            "success": "False",
            "error": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

#to delete any expense and adjust settlements
class DeleteexpView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        group = get_object_or_404(Tripgroup, id=request.data['group_id'])
        expen = get_object_or_404(addedexp, id=request.data['expense_id'], group=group)

        try:
            trip_mem = TripMember.objects.get(group=group, user=request.user)
        except TripMember.DoesNotExist:
            return Response({
                "success": "False",
                "error": "You are not a member of this group"
            }, status=status.HTTP_403_FORBIDDEN)

        tosettle.objects.filter(connect=expen).delete()

        return Response({
            "success": "True",
            "message": "Expense deleted and settlements adjusted successfully!"
        }, status=status.HTTP_200_OK)

#to mark a debt as paid and delete the settlement
class SettlementView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        group_id = request.data['group_id']
        exp_id=request.data['exp_id']
        addexp= get_object_or_404(addedexp, id=exp_id)
        user= request.user
        settlement = get_object_or_404(tosettle, group_id=group_id,connect=addexp, debter=user)
        if not settlement:
            return Response({
                "success": "False",
                "error": "No settlement found for this user"
            }, status=status.HTTP_400_BAD_REQUEST)
        if settlement.debter != user:
            return Response({
                "success": "False",
                "error": "You are not authorized to mark this debt as paid."
            }, status=status.HTTP_403_FORBIDDEN)

        settlement.is_paid= True
        settlement.save()
        email_for_paying(settlement.debter , settlement.creditor, settlement.debtamount, settlement.connect)
        return Response({
            "success": "True",
            "message": "Debt paid and settlement deleted successfully!"
        }, status=status.HTTP_200_OK)
       
#to view all the details of a group
class GroupDetailsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request,id, *args, **kwargs):
        group_id = id
        group = get_object_or_404(Tripgroup, id=id)
        expenses = addedexp.objects.filter(group=group).select_related( 'group','paidby' )
        group_serializer = TripgroupgetSerializer(group)

        expense_serializer = AddedExpgetSerializer(expenses, many=True, context={'request': request})

        response_data = {
            "group": group_serializer.data,
            "expenses": expense_serializer.data
        }
        return Response(response_data, status=status.HTTP_200_OK)
    
#to view all the settlements of a group
class GroupSettlementsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id, *args, **kwargs):
        group = get_object_or_404(Tripgroup, id=id)
        settlements = tosettle.objects.filter(group=group)   
        serializer = ToSettlegetSerializer(settlements, many=True)
        return Response({
            "success": "True",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

class UserTripGroupsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
       
        trip_groups=Tripgroup.objects.filter(tripmember__user=request.user).annotate(
         members_count=Count('members')
         )
        serializer = TripgroupSummarySerializer(trip_groups, many=True)
        return Response({
            "success": True,
            "data": serializer.data
        }, status=status.HTTP_200_OK)
    
class GroupMembersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id, *args, **kwargs):
        group = get_object_or_404(Tripgroup, id=id)
        group_members = TripMember.objects.filter(group=group).select_related('user')
        serializer = TripMembergetSerializer(group_members, many=True)
        return Response({
            "success": True,
            "data": serializer.data
        }, status=status.HTTP_200_OK)
    
class CreateDebtView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = DebtSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({
                "success": "True",
                "message": "Debt created successfully!"
            }, status=status.HTTP_201_CREATED)
        return Response({
            "success": "False",
            "error": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    

class DebtListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        if start_date and end_date:
            start_date = parse_date(start_date)
            end_date = parse_date(end_date)

            if not start_date or not end_date:
                return Response({
                    "success": "False",
                    "error": "Invalid date format"
                }, status=status.HTTP_400_BAD_REQUEST)

            debts = Debt.objects.filter(user=request.user, date__range=[start_date, end_date]).order_by('-date', '-time')
        else:
            debts = Debt.objects.filter(user=request.user).order_by('-date', '-time')

        serializer = DebtSerializer(debts, many=True)
        return Response({
            "success": "True",
            "data": serializer.data
        }, status=status.HTTP_200_OK)
    

class MarkDebtAsPaidView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        if not request.data.get('debt_id'):
            return Response({
                "success": "False",
                "error": "Debt ID is required"
            }, status=status.HTTP_400_BAD_REQUEST)

        debt_id = request.data['debt_id']
        debt = get_object_or_404(Debt, id=debt_id, user=request.user)

        if debt.is_paid:
            return Response({
                "success": "False",
                "error": "Debt is already marked as paid"
            }, status=status.HTTP_400_BAD_REQUEST)

        debt.is_paid = True
        debt.save()
        if debt.lend is False:
          expenses.objects.create(user=request.user, amount= debt.amount , category="Debts" )
        else:
            expenses.objects.create(user=request.user, amount= debt.amount , category="Debts" , is_credit=True)
        serializer = DebtSerializer(debt)
        return Response({
            "success": "True",
            "message": "Debt marked as paid successfully",
        }, status=status.HTTP_200_OK)
    

class UsershareView(APIView):
    permission_classes=[IsAuthenticated]

    def get(self, request , id , *args , **kwargs):
        user=request.user
        group_id=id
        group= get_object_or_404(Tripgroup, id=group_id)
        try:
            trip_mem = TripMember.objects.get(group=group, user=request.user)
        except :
            return Response({
                "success": "False",
                "error": "You are not a member of this group"
            }, status=status.HTTP_403_FORBIDDEN)
        
        shares=[]
        members = TripMember.objects.filter(group=group).select_related('group')
        for member in members :
            
            if member.user != user:
                
                creditor_sum = tosettle.objects.filter(
                    group=group,
                    creditor=user,
                    debter=member.user,
                    is_paid=False
                ).aggregate(total=Sum('debtamount'))['total'] or 0
                
                debter_sum = tosettle.objects.filter(
                    group=group,
                    debter=user,
                    creditor=member.user,
                    is_paid=False
                ).aggregate(total=Sum('debtamount'))['total'] or 0
                
               
                shares.append({
                    "member": member.user.email,
                     "money": creditor_sum - debter_sum
                })

        return Response({
            "success": True,
            "user_shares": shares
        }, status=status.HTTP_200_OK)

class GroupAmountsView(APIView):
    permission_classes=[IsAuthenticated]

    def get(self, request, id, *args, **kwargs):
        user=request.user
        group_id=id
        group= get_object_or_404(Tripgroup, id=group_id)
        try:
            trip_mem = TripMember.objects.get(group=group, user=request.user)
        except :
            return Response({
                "success": "False",
                "error": "You are not a member of this group"
            }, status=status.HTTP_403_FORBIDDEN)
        
        personamount=[]
        members= TripMember.objects.filter(group=group)
        for member in members:
             totalsum = addedexp.objects.filter(
                    group=group,
                    paidby=member.user,
                ).aggregate(total=Sum('amount'))['total'] or 0
             
             personamount.append({
                 "member": member.user.email,
                  "money": totalsum
                })
             
        return Response({
            "success":"True",
            "personshare":personamount
        }, status=status.HTTP_200_OK)
       