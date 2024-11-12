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

class DashboardView(APIView):
  permission_classes = [IsAuthenticated]  

  def get(self,request, *args, **kwargs):
    groups = Group.objects.filter(groupowner=request.user).annotate(member_count=Count('groupmember'))
    othergrps = Group.objects.exclude(groupowner=request.user).annotate(member_count=Count('groupmember'))
    debt_amount = BillParticipant.objects.filter(participant=request.user, paid=False).aggregate(total_debt=Sum('amount'))['total_debt'] or 0
    amount_topay = BillParticipant.objects.filter(bill__billowner=request.user, paid=False).aggregate(total_owed=Sum('amount'))['total_owed'] or 0

    context = {
        'owner groups': groups,
        'members groups': othergrps,
        'debt_amount': debt_amount,
        'amount_owed': amount_topay
    }
    return Response(status=status.HTTP_200_OK, data=context)
  
  
class AddGroupView(CreateAPIView):
        permission_classes = [IsAuthenticated]
        serializer_class = GroupSerializer

        def post(self, request, *args, **kwargs):
            name = request.data['name']
            if name == "":
                return Response({ "success" : "False",
                    "error": "Group name cannot be empty"}, status=status.HTTP_400_BAD_REQUEST)
            serializer= GroupSerializer(data=request.data,  context={'request': request})
            if serializer.is_valid():
                serializer.save(groupowner=request.user)
                
                return Response({
                    "success": "True",
                    "message": "Group created successfully"
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    "success": "False",
                    "error": serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
            
class AddGroupMemberView(CreateAPIView):
        permission_classes = [IsAuthenticated]
        serializer_class = GroupMemberSerializer

        def post(self, request, *args, **kwargs):
            group_id = request.data['group']
            group = Group.objects.filter(id=group_id).first()
            if group is None:
                return Response({ "success" : "False",
                    "error": "Group not found"}, status=status.HTTP_400_BAD_REQUEST)
            serializer= GroupMemberSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "success": "True",
                    "message": "Member added to group successfully"
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    "success": "False",
                    "error": serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)