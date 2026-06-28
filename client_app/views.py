import datetime
import json

# ==================================================
# EV Point - Client Module Views
# Handles station search, booking management, and dashboard operations
# ==================================================

from django.contrib import messages
from django.db import IntegrityError, transaction
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.utils import timezone

from owner_app.models import EVStation
from staff_app.models import StationSlotStatus
from .models import Booking

# ==================================================
# Charging Slot Time Generation
# Creates hourly charging slots from 6 AM to 6 AM next day
# ==================================================

SLOT_TIMES = []
for h in range(6, 30):
    start_hour = h % 24
    end_hour = (h + 1) % 24
    period_start = 'AM' if start_hour < 12 else 'PM'
    period_end = 'AM' if end_hour < 12 else 'PM'
    display_start = 12 if start_hour % 12 == 0 else start_hour % 12
    display_end = 12 if end_hour % 12 == 0 else end_hour % 12
    SLOT_TIMES.append({
        'slot_name': f'Slot {len(SLOT_TIMES) + 1}',
        'start_time': f'{display_start:02d}:00 {period_start}',
        'end_time': f'{display_end:02d}:00 {period_end}',
        'time': f'{display_start:02d}:00 {period_start} - {display_end:02d}:00 {period_end}',
        'absolute_start_hour': h,
        'absolute_end_hour': h + 1,
    })


def slot_end_datetime(booking_date, slot_definition):
    end_at = datetime.datetime.combine(booking_date, datetime.time.min) + datetime.timedelta(
        hours=slot_definition['absolute_end_hour']
    )
    return timezone.make_aware(end_at, timezone.get_current_timezone())


def slot_has_ended(booking_date, slot_definition, current_time=None):
    if current_time is None:
        current_time = timezone.localtime()
    return slot_end_datetime(booking_date, slot_definition) <= current_time

# ==================================================
# Client Dashboard View
# Displays the main dashboard for EV Point clients
# ==================================================
def client_dashboard(request):

    return render(request,'client_dashboard.html' )

# ==================================================
# Membership Plans View
# Displays available subscription plans for users
# ==================================================
def plans_list(request):
    return render(request, 'plans_list.html')

# ==================================================
# Station Search View
# Displays all active EV charging stations
# ==================================================
def station_search(request):

    # Retrieve all active charging stations
    stations = EVStation.objects.filter(

        is_active=True

    )

    return render(

        request,

        'station_search.html',

        {

            'stations': stations
 
        }
    )


# ==================================================
# Book Charging Slot View
# Handles slot booking and availability management
# ==================================================
def book_now(request, station_id):
    # Retrieve selected charging station
    station = get_object_or_404(EVStation, station_id=station_id, is_active=True)
    # Generate next 7 booking dates
    today = timezone.localdate()
    current_time = timezone.localtime()
    date_list = [today + datetime.timedelta(days=i) for i in range(7)]
    # Fetch existing bookings for selected dates
    booked_slots = Booking.objects.filter(
        station=station,
        date__in=date_list,
    ).exclude(status=Booking.Status.CANCELLED)
    booked_lookup = {(booking.date, booking.slot_name): booking for booking in booked_slots}
    unavailable_slot_ids = set(
        StationSlotStatus.objects.filter(station=station)
        .exclude(status=StationSlotStatus.Status.AVAILABLE)
        .values_list('slot_id', flat=True)
    )

    # Process booking form submission
    if request.method == 'POST':
        if station.operational_status != EVStation.OperationalStatus.OPEN:
            messages.error(request, 'This station is not currently open for bookings.')
            return redirect('book_now', station_id=station_id)

        # Retrieve selected slot details from form
        selected_date = request.POST.get('selected_date')
        selected_slot = request.POST.get('selected_slot')
        selected_start = request.POST.get('selected_start')
        selected_end = request.POST.get('selected_end')

        if not selected_date or not selected_slot:
            messages.error(request, 'Choose a date and slot before booking.')
            return redirect('book_now', station_id=station_id)

        # Validate booking date format
        try:
            booking_date = datetime.datetime.strptime(selected_date, '%Y-%m-%d').date()
        except ValueError:
            messages.error(request, 'Invalid booking date.')
            return redirect('book_now', station_id=station_id)

        if booking_date not in date_list:
            messages.error(request, 'Bookings are available only for the next 7 days.')
            return redirect('book_now', station_id=station_id)

        valid_slots = {slot['slot_name']: (index, slot) for index, slot in enumerate(SLOT_TIMES)}
        if selected_slot not in valid_slots:
            messages.error(request, 'Invalid charging slot.')
            return redirect('book_now', station_id=station_id)
        slot_index, canonical_slot = valid_slots[selected_slot]
        database_slot_id = 201 + slot_index
        if slot_has_ended(booking_date, canonical_slot, current_time=current_time):
            messages.error(request, 'This charging slot has already ended and cannot be booked.')
            return redirect('book_now', station_id=station_id)
        if database_slot_id in unavailable_slot_ids:
            messages.error(request, 'This charging slot is currently unavailable.')
            return redirect('book_now', station_id=station_id)

        # Prevent duplicate slot bookings
        if Booking.objects.filter(
            station=station,
            date=booking_date,
            slot_name=selected_slot,
        ).exclude(status=Booking.Status.CANCELLED).exists():
            messages.error(request, 'This slot is already booked. Please choose another slot.')
            return redirect('book_now', station_id=station_id)

        # Create new booking record
        try:
            with transaction.atomic():
                Booking.objects.create(
                    user=request.user,
                    station=station,
                    date=booking_date,
                    slot_name=selected_slot,
                    start_time=canonical_slot['start_time'],
                    end_time=canonical_slot['end_time'],
                )
        except IntegrityError:
            messages.error(request, 'This slot was just booked. Please choose another slot.')
            return redirect('book_now', station_id=station_id)

        # Display booking confirmation message
        messages.success(request, f'Booked {selected_slot} for {booking_date.strftime("%d %b %Y")} successfully.')
        return redirect('book_now', station_id=station_id)

    # Prepare slot availability data for frontend display
    slots_json = []
    for date in date_list:
        day_slots = []
        for index, slot in enumerate(SLOT_TIMES):
            if slot_has_ended(date, slot, current_time=current_time):
                continue
            if 201 + index in unavailable_slot_ids:
                status = 'unavailable'
            else:
                status = 'booked' if (date, slot['slot_name']) in booked_lookup else 'available'
            day_slots.append({
                'slot_name': slot['slot_name'],
                'time': slot['time'],
                'start_time': slot['start_time'],
                'end_time': slot['end_time'],
                'status': status,
            })
        slots_json.append(day_slots)

    # Render booking page with slot information
    return render(request, 'book_now.html', {
        'station': station,
        'slots_json': json.dumps(slots_json),
        'start_date': today.isoformat(),
    })



def my_bookings(request):
    bookings = Booking.objects.filter(user=request.user).select_related('station')
    return render(request, 'my_bookings.html', {'bookings': bookings})


@require_POST
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id, user=request.user)
    if booking.status not in (Booking.Status.PENDING, Booking.Status.CONFIRMED):
        messages.error(request, 'This booking can no longer be cancelled.')
    elif booking.date < datetime.date.today():
        messages.error(request, 'Past bookings cannot be cancelled.')
    else:
        booking.status = Booking.Status.CANCELLED
        booking.status_updated_at = timezone.now()
        booking.status_updated_by = request.user
        booking.save(update_fields=('status', 'status_updated_at', 'status_updated_by'))
        messages.success(request, f'Booking #{booking.pk} was cancelled.')
    return redirect('my_bookings')
