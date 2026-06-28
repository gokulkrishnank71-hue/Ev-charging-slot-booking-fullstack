from django.urls import include, path
from rest_framework.routers import DefaultRouter

from owner_app.apiviews import (
    ChargingSlotViewSet,
    EVStationViewSet,
    OwnerProfileViewSet,
)

router = DefaultRouter()
router.register("profiles", OwnerProfileViewSet, basename="owner-profile")
router.register("stations", EVStationViewSet, basename="station")
router.register(
    "charging-slots",
    ChargingSlotViewSet,
    basename="charging-slot",
)

urlpatterns = [
    path("", include(router.urls)),
]