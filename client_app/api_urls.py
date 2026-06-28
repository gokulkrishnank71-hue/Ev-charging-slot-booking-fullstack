from django.urls import include, path
from rest_framework.routers import DefaultRouter

from client_app.apiviews import (
    BookingViewSet,
    UserProfileViewSet,
)

router = DefaultRouter()
router.register(
    "profiles",
    UserProfileViewSet,
    basename="client-profile",
)
router.register(
    "bookings",
    BookingViewSet,
    basename="booking",
)

urlpatterns = [
    path("", include(router.urls)),
]