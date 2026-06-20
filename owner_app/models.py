from django.db import models
from django.conf import settings
from home.models import OwnerProfile

# ==================================================
# EV Point - Station Models
# Stores EV charging stations and charging slot details
# ==================================================

# ==================================================
# EV Charging Station Model
# Stores station information added by station owners
# ==================================================
class EVStation(models.Model):

    class OperationalStatus(models.TextChoices):
        OPEN = 'open', 'Open'
        CLOSED = 'closed', 'Closed'
        MAINTENANCE = 'maintenance', 'Under maintenance'
        OFFLINE = 'offline', 'Offline'

    # Unique station identifier
    station_id = models.AutoField(
        primary_key=True
    )

    # Owner associated with this charging station
    owner = models.ForeignKey(
        OwnerProfile,
        on_delete=models.CASCADE
    )

    # Name of the charging station
    station_name = models.CharField(max_length=100)

    # City where the station is located
    city = models.CharField(max_length=50)

    # Type of charging station
    station_type = models.CharField(max_length=50)

    # Total charging slots available
    total_slots = models.IntegerField()

    # Charging cost per unit
    rate_per_unit = models.DecimalField(
        max_digits=6,
        decimal_places=2
    )

    # Contact number of the station
    phone_number = models.CharField(max_length=10)

    # Indicates whether station is active or not
    is_active = models.BooleanField(default=False)

    # Live condition maintained by the owner or assigned station staff.
    operational_status = models.CharField(
        max_length=20,
        choices=OperationalStatus.choices,
        default=OperationalStatus.CLOSED,
    )
    status_message = models.CharField(max_length=200, blank=True)
    status_updated_at = models.DateTimeField(null=True, blank=True)
    status_updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='station_status_updates',
    )

    # Return station name for admin display
    def __str__(self):
        return self.station_name
    


# ==================================================
# Charging Slot Model
# Stores available charging time slots
# ==================================================
class chargingslot(models.Model):
    # Unique slot identifier
    slot_id = models.IntegerField(primary_key=True)
    # Name of the charging slot
    slot_name = models.CharField(max_length=50)
    # Slot start time
    start_time = models.CharField(max_length=20)
    # Slot end time
    end_time = models.CharField(max_length=20)

    # Return slot name for admin display
    def __str__(self):
        return self.slot_name
