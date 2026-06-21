from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from home.models import OwnerProfile

from .ownerserializer import OwnerSerializer


class OwnerQuerysetMixin:
    serializer_class = OwnerSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = OwnerProfile.objects.select_related('user').order_by('id')

        if self.request.user.is_staff:
            return queryset

        return queryset.filter(user=self.request.user)


class OwnerListAPIView(OwnerQuerysetMixin, generics.ListAPIView):
    pass


class OwnerDetailAPIView(OwnerQuerysetMixin, generics.RetrieveAPIView):
    pass