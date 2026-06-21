from rest_framework import serializers

from .models import StationStaffProfile


class StaffSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    station_id = serializers.IntegerField(read_only=True)
    station_name = serializers.CharField(
        source='station.station_name',
        read_only=True,
    )
    created_by_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = StationStaffProfile
        fields = [
            'id',
            'user_id',
            'username',
            'email',
            'station_id',
            'station_name',
            'created_by_id',
            'full_name',
            'phone',
            'employee_id',
            'is_active',
            'created_at',
        ]
        read_only_fields = fields