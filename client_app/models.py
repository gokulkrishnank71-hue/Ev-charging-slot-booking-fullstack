from django.conf import settings
from django.db import models
from django.db.models import Q
from owner_app.models import EVStation

# ==================================================
# EV Point - Booking Models
# Stores EV charging slot reservations made by users
# ==================================================

# ==================================================
# Booking Model
# Represents a charging slot reservation for a station
# ==================================================
class Booking(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        CONFIRMED = 'confirmed', 'Confirmed'
        CHARGING = 'charging', 'Charging'
        COMPLETED = 'completed', 'Completed'
        CANCELLED = 'cancelled', 'Cancelled'

    # User who made the booking
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    # EV charging station selected for booking
    station = models.ForeignKey(
        EVStation,
        on_delete=models.CASCADE
    )
    # Booking date
    date = models.DateField()
    # Name of the selected charging slot
    slot_name = models.CharField(max_length=50)
    # Slot start time
    start_time = models.CharField(max_length=20)
    # Slot end time
    end_time = models.CharField(max_length=20)
    # Timestamp when booking was created
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    status_updated_at = models.DateTimeField(null=True, blank=True)
    status_updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='booking_status_updates',
    )

    # Booking model configuration
    class Meta:
        # A cancelled reservation releases the slot for a new booking.
        constraints = [
            models.UniqueConstraint(
                fields=('station', 'date', 'slot_name'),
                condition=~Q(status='cancelled'),
                name='unique_active_booking_per_station_slot',
            ),
        ]
        # Display latest bookings first
        ordering = ['-date', 'slot_name']

    # Return readable booking information for admin display
    def __str__(self):
        return f'{self.user} - {self.station} - {self.date} - {self.slot_name}'
