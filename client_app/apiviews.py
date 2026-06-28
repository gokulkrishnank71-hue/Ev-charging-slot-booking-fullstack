from rest_framework import viewsets

from client_app.models import Booking
from client_app.userserializer import (
    BookingSerializer,
    UserProfileSerializer,
)
from home.models import UserProfile


class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.select_related("user").all()
    serializer_class = UserProfileSerializer


class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.select_related(
        "user",
        "station",
    ).all().order_by("-pk")
    serializer_class = BookingSerializer