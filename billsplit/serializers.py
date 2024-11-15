from rest_framework import serializers
from .models import Group, GroupMember, Bill, BillParticipant
from Authentication.models import User

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
    billowner = serializers.SlugRelatedField(slug_field='email', queryset=User.objects.all(), required=False)
    bill_participants =  BillParticipantSerializer(many=True,required=False)
    group = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all(), required=False)

    class Meta:
        model = Bill
        fields = ['id', 'group', 'amount', 'billname', 'billowner', 'bill_participants', 'billdate']

    def create(self, validated_data):
        request = self.context.get('request')
        group = self.context.get('group')
        billowner = request.user
        print(5)
        participants_data = validated_data.pop('bill_participants', [])
        bill = Bill.objects.create(
            group=group,
            billowner=billowner,
            **validated_data
        )
        print(6)
        for participant_data in participants_data:
            email = participant_data['participant']
            participant_user = User.objects.get(email=email)
            print(7)
            BillParticipant.objects.create(
                bill=bill,
                participant=participant_user,
                amount=participant_data['amount'],
               
            )
            print(8)
        return bill
    
