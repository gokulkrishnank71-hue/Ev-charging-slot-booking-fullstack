import datetime

from django.utils import timezone

from client_app.models import Booking
from owner_app.models import chargingslot

from .models import StationSlotStatus


BOOKING_PRESENTATION = {
    Booking.Status.PENDING: ('Booking pending', 'warning'),
    Booking.Status.CONFIRMED: ('Booked / Confirmed', 'primary'),
    Booking.Status.CHARGING: ('Charging', 'info'),
    Booking.Status.COMPLETED: ('Completed', 'success'),
}

CONDITION_PRESENTATION = {
    StationSlotStatus.Status.AVAILABLE: ('Available', 'success'),
    StationSlotStatus.Status.UNAVAILABLE: ('Unavailable', 'danger'),
    StationSlotStatus.Status.MAINTENANCE: ('Maintenance', 'warning'),
}


def booking_date_options():
    """Return the same seven-day booking window used by the client UI."""
    today = timezone.localdate()
    return [today + datetime.timedelta(days=offset) for offset in range(7)]


def selected_booking_date(raw_date):
    """Return a valid date from the booking window, defaulting to today."""
    available_dates = booking_date_options()
    try:
        selected_date = datetime.date.fromisoformat(raw_date) if raw_date else available_dates[0]
    except (TypeError, ValueError):
        selected_date = available_dates[0]

    if selected_date not in available_dates:
        selected_date = available_dates[0]
    return selected_date, available_dates


def build_slot_status_rows(station, selected_date):
    """Combine operational condition and active booking state for every slot."""
    slots = list(chargingslot.objects.order_by('slot_id'))
    condition_map = {
        condition.slot_id: condition
        for condition in StationSlotStatus.objects.filter(
            station=station,
            slot__in=slots,
        ).select_related('slot')
    }
    booking_map = {
        booking.slot_name: booking
        for booking in Booking.objects.filter(
            station=station,
            date=selected_date,
        ).exclude(status=Booking.Status.CANCELLED).select_related('user')
    }

    rows = []
    for slot in slots:
        condition = condition_map.get(slot.pk)
        condition_value = (
            condition.status if condition else StationSlotStatus.Status.AVAILABLE
        )
        condition_label, condition_badge = CONDITION_PRESENTATION[condition_value]
        booking = booking_map.get(slot.slot_name)

        if booking:
            booking_label, booking_badge = BOOKING_PRESENTATION.get(
                booking.status,
                (booking.get_status_display(), 'secondary'),
            )
        else:
            booking_label, booking_badge = 'Available', 'success'

        rows.append({
            'slot': slot,
            'station_status': condition,
            'condition_value': condition_value,
            'condition_label': condition_label,
            'condition_badge': condition_badge,
            'booking': booking,
            'booking_label': booking_label,
            'booking_badge': booking_badge,
        })
    return rows
