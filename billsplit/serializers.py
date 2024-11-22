from rest_framework import serializers
from .models import Group, GroupMember, Bill, BillParticipant
from Authentication.models import User
from django.shortcuts import get_object_or_404
from triptracker.models import tosettle
class GroupSerializer(serializers.ModelSerializer):
    members = serializers.SlugRelatedField(slug_field='email', many=True, queryset=User.objects.all(), required=False)
    groupowner= serializers.SlugRelatedField(slug_field='email',read_only=True)
    class Meta:
        model = Group
        fields = ['id', 'name', 'groupowner', 'members', 'created_at']

    def create(self, validated_data):
        request = self.context.get('request')
        if request is None:
            raise ValueError("Request object is required")
        members_data = validated_data.pop('members', [])
        group = Group.objects.create(name=validated_data['name'], groupowner=request.user)
        GroupMember.objects.create(group=group, member=request.user)
        for member in members_data:
            GroupMember.objects.create(group=group, member=member)
        return group

class GroupMemberSerializer(serializers.ModelSerializer):
   member = serializers.SlugRelatedField(slug_field='email', queryset=User.objects.all())

   class Meta:
        model = GroupMember
        fields = ['id', 'group', 'member', 'date_join']

class BillParticipantSerializer(serializers.ModelSerializer):
    participant = serializers.SlugRelatedField(slug_field='email', queryset=User.objects.all())
    bill = serializers.PrimaryKeyRelatedField(queryset=Bill.objects.all(), required=False)

    class Meta:
        model = BillParticipant
        fields = ['id', 'bill', 'participant', 'amount', 'paid']

class BillSerializer(serializers.ModelSerializer):
    bill_participants =  BillParticipantSerializer(many=True,required=False)
    
    class Meta:
        model = Bill
        fields = ['id', 'group', 'amount', 'billname', 'bill_participants', 'billdate']

    def create(self, validated_data):
        request = self.context.get('request')
        group = validated_data.get('group')
        billowner = request.user
        
        participants_data = validated_data.pop('bill_participants', [])
        bill = Bill.objects.create(
            billowner=billowner,
            **validated_data
        )
        bp = []
        for participant_data in participants_data:
            email = participant_data['participant']
            participant_user = get_object_or_404(User, email=email)
            percent=participant_data['amount']
            b = BillParticipant.objects.create(
                bill=bill,
                participant=participant_user,
                amount=((percent/100) * bill.amount)/request.user.currency_rate,
               
            )
            tosettle.objects.create(debtamount=((percent/100) * bill.amount)/request.user.currency_rate, debter=participant_user, creditor=billowner)
            bp += [b]
       
        validated_data["bill_participants"] = bp
   
        return bill
    
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'name','profile_image'] 

class BillParticipantget(serializers.ModelSerializer):
    participant = UserSerializer(read_only=True) 
    class Meta:
        model = BillParticipant
        fields = [ 'participant', 'amount', 'paid']


class BillgetSerializer(serializers.ModelSerializer):
    bill_participants = BillParticipantget(source='billparticipant_set', many=True, required=False)
    class Meta:
        model = Bill
        fields = ['id', 'group', 'amount', 'billname', 'bill_participants', 'billdate']

class GroupDetailSerializer(serializers.ModelSerializer):
    members = GroupMemberSerializer(source='groupmember_set', many=True, read_only=True)
    bills = BillgetSerializer(source='bill_set', many=True, read_only=True)

    class Meta:
        model = Group
        fields = ['id', 'name', 'groupowner', 'members', 'bills', 'created_at']