from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from home.models import UserProfile

from .userserializer import UserSerializer


class UserQuerysetMixin:
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = UserProfile.objects.select_related('user').order_by('id')

        if self.request.user.is_staff:
            return queryset

        return queryset.filter(user=self.request.user)


class UserListAPIView(UserQuerysetMixin, generics.ListAPIView):
    pass


class UserDetailAPIView(UserQuerysetMixin, generics.RetrieveAPIView):
    pass