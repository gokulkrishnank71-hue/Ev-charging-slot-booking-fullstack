from rest_framework import serializers

from client_app.models import Booking
from home.models import UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        source="user.username",
        read_only=True,
    )

    class Meta:
        model = UserProfile
        fields = "__all__"


class BookingSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        source="user.username",
        read_only=True,
    )
    station_name = serializers.CharField(
        source="station.station_name",
        read_only=True,
    )

    class Meta:
        model = Booking
        fields = "__all__"