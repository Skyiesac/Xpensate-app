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
import json
from django.utils.dateparse import parse_date
from django.db import transaction

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

    def post(self,request,id, *args, **kwargs):
         email=request.data['email']
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
         
         TripMember.objects.create(group=group, user=user)
         email_for_joining(email, group.name)
         return Response({
                "success": "True",
                "message": "Successfully joined the group"
            }, status=status.HTTP_200_OK)
 
    def delete(self, request, id , *args, **kwargs):
         email=request.data['email']
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
           trip_mem= TripMember.objects.get(group=group, user__email=request.data['paidby'])
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
                    if member.user!=user:
                        settlement, created = tosettle.objects.get_or_create(
                            group=group,
                            debter=member.user,
                            creditor=user,
                            defaults={'debtamount': debt_amount, 'connect': added_exp}
                        )
                        if not created:
                            settlement.debtamount += debt_amount
                            settlement.save()

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

        old_amount = expense.amount
        paidby= expense.paidby
        serializer = AddedExpSerializer(expense, data=request.data)
        if serializer.is_valid():
            with transaction.atomic():
                updated_exp = serializer.save()

                if old_amount != updated_exp.amount:
                    members = TripMember.objects.filter(group=group)
                    members_count = members.count()

                    new_debt_amount = updated_exp.amount / members_count
                    old_debt_amount = old_amount / members_count

                    for member in members:
                        if member.user != updated_exp.paidby:
                            settlement, created = tosettle.objects.get_or_create(
                                group=group,
                                debter=member.user,
                                creditor=paidby,
                                defaults={'debtamount': 0}
                            )
                            if not created:
                                settlement.debtamount -= old_debt_amount
                                if settlement.debtamount <= 0:
                                    settlement.delete()
                                else:
                                    settlement.save()

                            settlement, created = tosettle.objects.get_or_create(
                                group=group,
                                debter=member.user,
                                creditor=updated_exp.paidby,
                                defaults={'debtamount': new_debt_amount, 'connect': updated_exp}
                            )
                            if not created:
                                settlement.debtamount += new_debt_amount
                                settlement.save()
                             
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

        with transaction.atomic():
            members = TripMember.objects.filter(group=group)
            members_count = members.count()
            debt_amount = expen.amount / members_count

            for member in members:
                if member.user != expen.paidby:
                    settlement = tosettle.objects.get(group=group, debter=member.user, creditor=expen.paidby)
                    settlement.debtamount -= debt_amount
                    if settlement.debtamount <= 0:
                        settlement.delete()
                    else:
                        settlement.save()

            expen.delete()

        return Response({
            "success": "True",
            "message": "Expense deleted and settlements adjusted successfully!"
        }, status=status.HTTP_200_OK)

#to mark a debt as paid and delete the settlement
class SettlementView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        group_id = request.data['group_id']
        settle_id = request.data['settle_id']
        user= request.user
        settlement = get_object_or_404(tosettle, group_id=group_id,id= settle_id , debter=user)
        if not settlement:
            return Response({
                "success": "False",
                "error": "No settlement found for this user"
            }, status=status.HTTP_400_BAD_REQUEST)
        if settlement.creditor != user:
            return Response({
                "success": "False",
                "error": "You are not authorized to mark this debt as paid."
            }, status=status.HTTP_403_FORBIDDEN)

        settlement.delete()
        return Response({
            "success": "True",
            "message": "Debt paid and settlement deleted successfully!"
        }, status=status.HTTP_200_OK)
       
#to view all the details of a group
class GroupDetailsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request,id, *args, **kwargs):
        group_id = id
        try:
            group = Tripgroup.objects.get(id=group_id)

            group_serializer = TripgroupgetSerializer(group)
            
            expenses = addedexp.objects.filter(group=group)
            expense_serializer = AddedExpgetSerializer(expenses, many=True)
            
            response_data = {
                "group": group_serializer.data,
                "expenses": expense_serializer.data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        
        except Tripgroup.DoesNotExist:
            return Response({"error": "Group not found."}, status=status.HTTP_404_NOT_FOUND)
        
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

            debts = Debt.objects.filter(user=request.user, date__range=[start_date, end_date])
        else:
            debts = Debt.objects.filter(user=request.user)

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

        serializer = DebtSerializer(debt)
        return Response({
            "success": "True",
            "message": "Debt marked as paid successfully",
        }, status=status.HTTP_200_OK)