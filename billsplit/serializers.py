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
    group = serializers.SlugRelatedField(slug_field='name', queryset=Group.objects.all())
    member = serializers.SlugRelatedField(slug_field='email', queryset=User.objects.all())

    class Meta:
        model = GroupMember
        fields = ['id', 'group', 'member', 'date_join']


class BillParticipantSerializer(serializers.ModelSerializer):
    participant = serializers.SlugRelatedField(slug_field='email', queryset=User.objects.all())

    class Meta:
        model = BillParticipant
        fields = ['id', 'bill', 'participant', 'amount', 'paid']

class BillSerializer(serializers.ModelSerializer):
    group = serializers.SlugRelatedField(slug_field='name')
    billowner = serializers.SlugRelatedField(slug_field='email')
    bill_participants = BillParticipantSerializer(many=True, read_only=True)

    class Meta:
        model = Bill
        fields = ['id', 'group', 'amount', 'billname', 'billowner', 'bill_participants', 'billdate']