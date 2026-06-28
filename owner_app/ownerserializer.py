from rest_framework import serializers

from home.models import OwnerProfile
from owner_app.models import EVStation, chargingslot


class OwnerProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        source="user.username",
        read_only=True,
    )

    class Meta:
        model = OwnerProfile
        fields = "__all__"


class EVStationSerializer(serializers.ModelSerializer):
    owner_name = serializers.CharField(
        source="owner.owner_name",
        read_only=True,
    )

    class Meta:
        model = EVStation
        fields = "__all__"


class ChargingSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = chargingslot
        fields = "__all__"