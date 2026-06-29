from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from client_app.models import Booking
from client_app.userserializer import BookingSerializer, UserProfileSerializer
from home.models import UserProfile

class UserProfileViewSet(viewsets.ModelViewSet):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserProfile.objects.select_related("user").filter(user=self.request.user)

class BookingViewSet(viewsets.ModelViewSet):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Booking.objects.select_related("user", "station").filter(user=self.request.user).order_by("-pk")