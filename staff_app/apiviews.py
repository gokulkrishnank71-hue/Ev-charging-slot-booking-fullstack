from rest_framework import viewsets

from staff_app.models import (
    StationSlotStatus,
    StationStaffProfile,
)
from staff_app.staffserializer import (
    StationSlotStatusSerializer,
    StationStaffSerializer,
)


class StationStaffViewSet(viewsets.ModelViewSet):
    queryset = StationStaffProfile.objects.select_related(
        "user",
        "station",
        "created_by",
    ).all()
    serializer_class = StationStaffSerializer


class StationSlotStatusViewSet(viewsets.ModelViewSet):
    queryset = StationSlotStatus.objects.select_related(
        "station",
        "slot",
    ).all()
    serializer_class = StationSlotStatusSerializer