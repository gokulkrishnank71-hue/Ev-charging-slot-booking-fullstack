from rest_framework import viewsets

from home.models import OwnerProfile
from owner_app.models import EVStation, chargingslot
from owner_app.ownerserializer import (
    ChargingSlotSerializer,
    EVStationSerializer,
    OwnerProfileSerializer,
)


class OwnerProfileViewSet(viewsets.ModelViewSet):
    queryset = OwnerProfile.objects.select_related("user").all()
    serializer_class = OwnerProfileSerializer


class EVStationViewSet(viewsets.ModelViewSet):
    queryset = EVStation.objects.select_related("owner").all()
    serializer_class = EVStationSerializer


class ChargingSlotViewSet(viewsets.ModelViewSet):
    queryset = chargingslot.objects.all().order_by("slot_id")
    serializer_class = ChargingSlotSerializer