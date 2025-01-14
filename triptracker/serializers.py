from rest_framework import serializers
from .models import Tripgroup, TripMember, addedexp, tosettle, Debt
from Authentication.models import User
from billsplit.serializers import UserSerializer


class TripMemberSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(slug_field="email", queryset=User.objects.all())
    group = serializers.SlugRelatedField(
        slug_field="id", queryset=Tripgroup.objects.all()
    )

    class Meta:
        model = TripMember
        fields = ["user", "group", "joined_at"]


class TripgroupSerializer(serializers.ModelSerializer):
    members = TripMemberSerializer(many=True, read_only=True)
    invitecode = serializers.CharField(required=False, read_only=True)

    class Meta:
        model = Tripgroup
        fields = ["name", "members", "invitecode", "created_at"]


class AddedExpSerializer(serializers.ModelSerializer):
    paidby = serializers.SlugRelatedField(
        slug_field="email", queryset=User.objects.all()
    )
    group = serializers.SlugRelatedField(
        slug_field="id", queryset=Tripgroup.objects.all(), required=False
    )

    class Meta:
        model = addedexp
        fields = ["whatfor", "amount", "paidby", "group"]

    def create(self, validated_data):
        return addedexp.objects.create(**validated_data)


class ToSettleSerializer(serializers.ModelSerializer):
    debter = serializers.SlugRelatedField(
        slug_field="email", queryset=User.objects.all()
    )
    creditor = serializers.SlugRelatedField(
        slug_field="email", queryset=User.objects.all()
    )
    group = serializers.PrimaryKeyRelatedField(
        queryset=Tripgroup.objects.all(), required=False
    )
    connect = serializers.PrimaryKeyRelatedField(
        queryset=addedexp.objects.all(), required=False
    )

    class Meta:
        model = tosettle
        fields = ["debtamount", "debter", "creditor", "connect"]


class AddedExpgetSerializer(serializers.ModelSerializer):
    # paidby= paidbySerializer()
    paidby_email = serializers.SerializerMethodField()
    share = serializers.SerializerMethodField()
    is_paid = serializers.SerializerMethodField()

    class Meta:
        model = addedexp
        fields = ["id", "whatfor", "amount", "paidby_email", "share", "is_paid"]

    def get_paidby_email(self, obj):
        return obj.paidby.email

    def get_share(self, obj):
        request = self.context.get("request")
        user = request.user
        settlement = tosettle.objects.filter(connect=obj, debter=user).first()
        if settlement:
            return settlement.debtamount
        return False

    def get_is_paid(self, obj):
        request = self.context.get("request")
        user = request.user
        settlement = tosettle.objects.filter(connect=obj, debter=user).first()
        if settlement:
            return settlement.is_paid
        return False


class TripMembergetSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = TripMember
        fields = ["user"]


class TripgroupgetSerializer(serializers.ModelSerializer):
    members = TripMembergetSerializer(source="tripmember_set", many=True)

    class Meta:
        model = Tripgroup
        fields = ["id", "name", "invitecode", "created_at", "members"]


class ToSettlegetSerializer(serializers.ModelSerializer):
    creditor_email = serializers.SerializerMethodField()

    debter_email = serializers.SerializerMethodField()

    class Meta:
        model = tosettle
        fields = ["debtamount", "debter_email", "creditor_email"]

    def get_creditor_email(self, obj):
        return obj.creditor.email

    def get_debter_email(self, obj):
        return obj.debter.email


class DebtSerializer(serializers.ModelSerializer):
    class Meta:
        model = Debt
        fields = [
            "id",
            "user",
            "name",
            "amount",
            "description",
            "date",
            "time",
            "lend",
            "is_paid",
        ]
        read_only_fields = ["user"]

    def create(self, validated_data):
        request = self.context.get("request")
        user = request.user
        validated_data["user"] = user

        currency_rate = user.currency_rate
        validated_data["amount"] = validated_data["amount"]

        return super().create(validated_data)


class TripgroupSummarySerializer(serializers.ModelSerializer):
    members_count = serializers.SerializerMethodField()

    class Meta:
        model = Tripgroup
        fields = ["id", "name", "invitecode", "members_count"]

    def get_members_count(self, obj):
        return obj.members_count
