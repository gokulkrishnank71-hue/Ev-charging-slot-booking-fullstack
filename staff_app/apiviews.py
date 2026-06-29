from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from staff_app.models import StationSlotStatus, StationStaffProfile
from staff_app.staffserializer import StationSlotStatusSerializer, StationStaffSerializer


class StationStaffViewSet(viewsets.ModelViewSet):
    serializer_class = StationStaffSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return StationStaffProfile.objects.select_related(
            "user",
            "station",
            "created_by",
        ).filter(user=self.request.user)


class StationSlotStatusViewSet(viewsets.ModelViewSet):
    serializer_class = StationSlotStatusSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return StationSlotStatus.objects.select_related(
            "station",
            "slot",
        ).filter(station__staff_members__user=self.request.user)