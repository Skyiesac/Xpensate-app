from rest_framework import serializers
from .models import Tripgroup, TripMember, addedexp, tosettle
from Authentication.models import User


class TripMemberSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(slug_field='email', queryset=User.objects.all())
    group = serializers.SlugRelatedField(slug_field='name', queryset=Tripgroup.objects.all())

    class Meta:
        model = TripMember
        fields = ['user', 'group', 'joined_at']

class TripgroupSerializer(serializers.ModelSerializer):
    members = TripMemberSerializer(many=True, read_only=True)
    invitecode = serializers.CharField(required=False, read_only=True)

    class Meta:
        model = Tripgroup
        fields = ['name', 'members', 'invitecode', 'created_at']

class AddedExpSerializer(serializers.ModelSerializer):
    paidby = serializers.SlugRelatedField(slug_field='email', queryset=User.objects.all())

    class Meta:
        model = addedexp
        fields = ['whatfor', 'amount', 'paidby']

class ToSettleSerializer(serializers.ModelSerializer):
    debter = serializers.SlugRelatedField(slug_field='email', queryset=User.objects.all())
    creditor = serializers.SlugRelatedField(slug_field='email', queryset=User.objects.all())

    class Meta:
        model = tosettle
        fields = ['debtamount', 'debter', 'creditor']