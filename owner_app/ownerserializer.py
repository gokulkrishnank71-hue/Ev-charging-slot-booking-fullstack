from rest_framework import serializers

from home.models import OwnerProfile


class OwnerSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = OwnerProfile
        fields = [
            'id',
            'user_id',
            'username',
            'email',
            'owner_name',
            'phone',
        ]
        read_only_fields = fields