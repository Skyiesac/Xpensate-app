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
from django.db import transaction

# Create your views here.
class CreateGroupView(APIView):
        permission_classes = [IsAuthenticated]

        def post(self, request, *args, **kwargs):
            name = request.data['name']
            if not name:
                return Response({ "success" : "False",
                    "error": "Group name cannot be empty"}, status=status.HTTP_400_BAD_REQUEST)
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


class JoinwcodeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        invitecode = request.data.get('invitecode')
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
            

class CreateexpView(APIView):
    permission_classes=[IsAuthenticated]

    def post(self, request,id, *args , **kwargs):
        group= get_object_or_404(Tripgroup, id=id)
        email=request.data['email']
        try:
           trip_mem= TripMember.objects.get(group=group, user__email=email)
        except :
            return Response({
                "success": "False",
                "error": "Email does not exist in the members of this group"
            }, status=status.HTTP_400_BAD_REQUEST)

        user= trip_mem.user
        data = request.data.copy()
        data['group'] = group.id
        data['paidby']=user

        serializer = AddedExpSerializer(data=data)
        if serializer.is_valid():
            with transaction.atomic():
                added_exp = serializer.save(paidby=user)
                members = TripMember.objects.filter(group=group)
                memberscnt=members.count()
                debt_amount= added_exp.amount / memberscnt

                for member in members:
                    if member.user!=user:
                        tosettle.objects.create(
                            group=group,
                            debtamount=debt_amount,
                            debter=member.user,
                            creditor=user,
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
        

class EditexpView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, id, *args, **kwargs):
        added_exp = get_object_or_404(addedexp, id=id)
        group = added_exp.group
        email = request.data.get('email')

        try:
            trip_mem = TripMember.objects.get(group=group, user__email=email)
        except TripMember.DoesNotExist:
            return Response({
                "success": "False",
                "error": "Email does not exist in the members of this group"
            }, status=status.HTTP_400_BAD_REQUEST)

        user = trip_mem.user
        data = request.data.copy()
        data['group'] = group.id
        data['paidby'] = user

        serializer = AddedExpSerializer(added_exp, data=data)
        if serializer.is_valid():
            with transaction.atomic():

                added_exp = serializer.save(paidby=user)

                tosettle.objects.filter(connect=added_exp).delete()

                members = TripMember.objects.filter(group=group)
                memberscnt = members.count()
                debt_amount = added_exp.amount / memberscnt

                for member in members:
                    if member.user != user:
                        tosettle.objects.create(
                            group=group,
                            debtamount=debt_amount,
                            debter=member.user,
                            creditor=user,
                            connect=added_exp
                        )

                return Response({
                    "success": "True",
                    "message": "Expense updated and settlements created successfully!"
                }, status=status.HTTP_200_OK)
        else:
            return Response({
                "success": "False",
                "error": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)