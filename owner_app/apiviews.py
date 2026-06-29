from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from home.models import OwnerProfile
from owner_app.models import EVStation, chargingslot
from owner_app.ownerserializer import (
    ChargingSlotSerializer,
    EVStationSerializer,
    OwnerProfileSerializer,
)


class OwnerProfileViewSet(viewsets.ModelViewSet):
    serializer_class = OwnerProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return OwnerProfile.objects.select_related("user").filter(user=self.request.user)


class EVStationViewSet(viewsets.ModelViewSet):
    serializer_class = EVStationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return EVStation.objects.select_related("owner").filter(owner__user=self.request.user)


class ChargingSlotViewSet(viewsets.ModelViewSet):
    queryset = chargingslot.objects.all().order_by("slot_id")
    serializer_class = ChargingSlotSerializer
    permission_classes = [IsAuthenticated]