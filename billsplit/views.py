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

class DashboardView(APIView):
  permission_classes = [IsAuthenticated]  

  def get(self,request, *args, **kwargs):
    groups = Group.objects.filter(groupowner=request.user).annotate(member_count=Count('groupmember'))
    othergrps = Group.objects.exclude(groupowner=request.user).filter(groupmember__member=request.user).annotate(member_count=Count('groupmember'))
    debt_amount = BillParticipant.objects.filter(participant=request.user, paid=False).aggregate(total_debt=Sum('amount'))['total_debt'] or 0
    amount_topay = BillParticipant.objects.filter(bill__billowner=request.user, paid=False).aggregate(total_owed=Sum('amount'))['total_owed'] or 0

    groups_serializer = GroupSerializer(groups, many=True)
    othergroups_serializer = GroupSerializer(othergrps, many=True)

    context = {
        'owner groups': groups_serializer.data,
        'members groups': othergroups_serializer.data,
        'debt_amount': debt_amount,
        'amount_owed': amount_topay
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

    def post(self, request,id, *args, **kwargs):
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
                    "error": "Only the group owner can create bills"
                }, status=status.HTTP_403_FORBIDDEN)

      

        