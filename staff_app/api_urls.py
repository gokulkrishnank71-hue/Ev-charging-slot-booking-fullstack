from django.urls import include, path
from rest_framework.routers import DefaultRouter

from staff_app.apiviews import (
    StationSlotStatusViewSet,
    StationStaffViewSet,
)

router = DefaultRouter()
router.register("staff", StationStaffViewSet, basename="staff")
router.register(
    "slot-statuses",
    StationSlotStatusViewSet,
    basename="slot-status",
)

urlpatterns = [
    path("", include(router.urls)),
]