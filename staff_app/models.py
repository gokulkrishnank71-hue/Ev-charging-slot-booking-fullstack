from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from home.models import OwnerProfile
from owner_app.models import EVStation, chargingslot


class StationStaffProfile(models.Model):
    """An operational user assigned to one EV charging station."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='station_staff_profile',
    )
    station = models.ForeignKey(
        EVStation,
        on_delete=models.CASCADE,
        related_name='staff_members',
    )
    created_by = models.ForeignKey(
        OwnerProfile,
        on_delete=models.CASCADE,
        related_name='created_staff_members',
    )
    full_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    employee_id = models.CharField(max_length=30)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('station', 'employee_id'),
                name='unique_employee_id_per_station',
            ),
        ]
        ordering = ('station__station_name', 'full_name')

    def __str__(self):
        return f'{self.full_name} - {self.station.station_name}'

    def clean(self):
        super().clean()
        if self.station_id and self.created_by_id and self.station.owner_id != self.created_by_id:
            raise ValidationError({'station': 'Staff can only be assigned by this station owner.'})


class StationSlotStatus(models.Model):
    class Status(models.TextChoices):
        AVAILABLE = 'available', 'Available'
        UNAVAILABLE = 'unavailable', 'Unavailable'
        MAINTENANCE = 'maintenance', 'Maintenance'

    station = models.ForeignKey(
        EVStation,
        on_delete=models.CASCADE,
        related_name='slot_statuses',
    )
    slot = models.ForeignKey(
        chargingslot,
        on_delete=models.CASCADE,
        related_name='station_statuses',
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.AVAILABLE,
    )
    note = models.CharField(max_length=200, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='slot_status_updates',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('station', 'slot'),
                name='unique_slot_status_per_station',
            ),
        ]
        ordering = ('slot__slot_id',)

    def __str__(self):
        return f'{self.station} - {self.slot}: {self.get_status_display()}'
