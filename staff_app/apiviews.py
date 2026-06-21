from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from .models import StationStaffProfile
from .staffserializer import StaffSerializer


class StaffQuerysetMixin:
    serializer_class = StaffSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = StationStaffProfile.objects.select_related(
            'user',
            'station',
            'created_by',
        ).order_by('id')

        user = self.request.user

        if user.is_staff:
            return queryset

        owner = getattr(user, 'ownerprofile', None)
        if owner:
            return queryset.filter(created_by=owner)

        staff_profile = getattr(user, 'station_staff_profile', None)
        if staff_profile:
            return queryset.filter(pk=staff_profile.pk)

        return queryset.none()


class StaffListAPIView(StaffQuerysetMixin, generics.ListAPIView):
    pass


class StaffDetailAPIView(StaffQuerysetMixin, generics.RetrieveAPIView):
    pass