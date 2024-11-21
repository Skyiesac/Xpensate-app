from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated ,AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import serializers, status
from .serializers import *
from .models import *
from rest_framework.generics import *
from django.db.models import Count, Sum
from .models import *
import json
from django.db.models import Q
from expense.models import expenses

class AllGroupsView(APIView):
  permission_classes = [IsAuthenticated]  

  def get(self,request, *args, **kwargs):
    groups = Group.objects.filter(groupowner=request.user).annotate(member_count=Count('groupmember'))
    othergrps = Group.objects.exclude(groupowner=request.user).filter(groupmember__member=request.user).annotate(member_count=Count('groupmember'))
    
    groups_serializer = GroupSerializer(groups, many=True)
    othergroups_serializer = GroupSerializer(othergrps, many=True)

    context = {
        'owner groups': groups_serializer.data,
        'members groups': othergroups_serializer.data,
       
    }
    return Response(status=status.HTTP_200_OK, data=context)
  
  
class AddGroupView(CreateAPIView):
        permission_classes = [IsAuthenticated]
        serializer_class = GroupSerializer

        def post(self, request, *args, **kwargs):
            name = request.data['name']
            if not name:
                return Response({ "success" : "False",
                    "error": "Group name cannot be empty"}, status=status.HTTP_400_BAD_REQUEST)
            serializer= GroupSerializer(data=request.data,  context={'request': request})
            if serializer.is_valid():
                serializer.save(groupowner=request.user)
                
                return Response({
                    "success": "True",
                    "message": "Group created successfully!"
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    "success": "False",
                    "error": serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
            
class AddRemoveMemberView(APIView):
        permission_classes = [IsAuthenticated]
        serializer_class = GroupMemberSerializer

        def post(self, request,id, *args, **kwargs):
            group_id = id
            group = Group.objects.get(id=group_id)
            if group is None:
                return Response({ "success" : "False",
                    "error": "Group not found"}, status=status.HTTP_400_BAD_REQUEST)
            
            if group.groupowner != request.user:
                return Response({
                    "success": "False",
                    "error": "Only the group owner can add members"
                }, status=status.HTTP_403_FORBIDDEN)

            serializer = GroupMemberSerializer(data=request.data)
            if serializer.is_valid():
                email = serializer.validated_data['member']
                member = User.objects.get(email=email)
                if member is None:
                    return Response({
                        "success": "False",
                        "error": "User with email not found"
                    }, status=status.HTTP_400_BAD_REQUEST)

                GroupMember.objects.create(group=group, member=member)
                return Response({
                    "success": "True",
                    "message": "Member added to group successfully"
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    "success": "False",
                    "error": serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)

        #to remove the member from the group  
        def delete(self, request, id, *args, **kwargs):
            group_id = id
            group = Group.objects.get(id=group_id)
            if group is None:
                return Response({
                    "success": "False",
                    "error": "Group not found"
                }, status=status.HTTP_400_BAD_REQUEST)

            if group.groupowner != request.user:
                return Response({
                    "success": "False",
                    "error": "Only the group owner can remove members"
                }, status=status.HTTP_403_FORBIDDEN)

            email = request.data.get('member')
            member = User.objects.filter(email=email).first()
            if member is None:
                return Response({
                    "success": "False",
                    "error": "User with this email not found"
                }, status=status.HTTP_400_BAD_REQUEST)

            groupmember = GroupMember.objects.filter(group=group, member=member).first()
            if groupmember is None:
                return Response({
                    "success": "False",
                    "error": "Group member not found"
                }, status=status.HTTP_400_BAD_REQUEST)

            groupmember.delete()
            return Response({
                "success": "True",
                "message": "Member removed from group successfully"
            }, status=status.HTTP_200_OK)


class CreateBillView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = BillSerializer

    def post(self, request , *args, **kwargs):
        bill_serializer = BillSerializer(data=request.data, context={'request': request})
        if not bill_serializer.is_valid():
            return Response({
                "success": "False",
                "error": bill_serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        group = bill_serializer.validated_data['group']

        if group is None:
            return Response({
                "success": "False",
                "error": "Group not found"
            }, status=status.HTTP_400_BAD_REQUEST)

        if group.groupowner != request.user:
            return Response({
                "success": "False",
                "error": "Only the group owner can create bills"
            }, status=status.HTTP_403_FORBIDDEN)

        bill = bill_serializer.save()

        return Response({
            "success": "True",
            "message": "Bill and participants added successfully",
        }, status=status.HTTP_201_CREATED)



class MarkAsPaidView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id, *args, **kwargs):
        bill = get_object_or_404(Bill, id=id)
        email=request.data['email']
        if request.user != bill.billowner:
            return Response({
                "success": "False",
                "error": "Only the bill owner can mark participants as paid"
            }, status=status.HTTP_403_FORBIDDEN)
        if not email:
            return Response({
                "success": "False",
                "error": "Participant email is required"
            }, status=status.HTTP_400_BAD_REQUEST)

        participant = get_object_or_404(User, email=email)
        
        billparticipant = get_object_or_404(BillParticipant, bill=bill, participant=participant)
        billparticipant.paid = True
        billparticipant.save()
        if billparticipant.participant == bill.billowner:
           expenses.objects.create(user=participant, amount=billparticipant.amount, category="Bill Payment", is_credit=False)
        else:
            expenses.objects.create(user=participant, amount=billparticipant.amount, category="Bill Payment", is_credit=False)
            expenses.objects.create(user=request.user, amount=billparticipant.amount, category="Bill Payment", is_credit=True)
        return Response({
            "success": "True",
            "message": "Participant marked as paid successfully"
        }, status=status.HTTP_200_OK)
    
class RecentsplitsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        bills = Bill.objects.filter(billparticipant__participant=user).order_by('-billdate')
        serializer = BillgetSerializer(bills, many=True)
        return Response({
            "success": "True",
              "data": serializer.data,
        }, status=status.HTTP_200_OK)
    
class GroupDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id, *args, **kwargs):
        group = get_object_or_404(Group, id=id)
        
        serializer = GroupDetailSerializer(group)
        return Response({
            "success": True,
            "data": serializer.data
        }, status=status.HTTP_200_OK)
    
