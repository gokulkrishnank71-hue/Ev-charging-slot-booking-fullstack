from rest_framework import serializers

from staff_app.models import (
    StationSlotStatus,
    StationStaffProfile,
)


class StationStaffSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        source="user.username",
        read_only=True,
    )
    station_name = serializers.CharField(
        source="station.station_name",
        read_only=True,
    )

    class Meta:
        model = StationStaffProfile
        fields = "__all__"


class StationSlotStatusSerializer(serializers.ModelSerializer):
    station_name = serializers.CharField(
        source="station.station_name",
        read_only=True,
    )
    slot_name = serializers.CharField(
        source="slot.slot_name",
        read_only=True,
    )

    class Meta:
        model = StationSlotStatus
        fields = "__all__"