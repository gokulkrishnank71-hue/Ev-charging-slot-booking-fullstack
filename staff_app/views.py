from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.urls import reverse
from django.views.decorators.http import require_POST

from client_app.models import Booking
from owner_app.models import EVStation, chargingslot

from .models import StationSlotStatus
from .slot_status import build_slot_status_rows, selected_booking_date


def _dashboard_redirect(request):
    raw_date = request.POST.get('selected_date')
    if raw_date:
        selected_date, _ = selected_booking_date(raw_date)
        return redirect(f'{reverse("staff_dashboard")}?date={selected_date.isoformat()}')
    return redirect('staff_dashboard')


def staff_login(request):
    if request.user.is_authenticated and hasattr(request.user, 'station_staff_profile'):
        profile = request.user.station_staff_profile
        if profile.is_active:
            return redirect('staff_dashboard')

    if request.method == 'POST':
        user = authenticate(
            request,
            username=request.POST.get('username', '').strip(),
            password=request.POST.get('password', ''),
        )
        if user is not None and hasattr(user, 'station_staff_profile'):
            profile = user.station_staff_profile
            if profile.is_active:
                auth_login(request, user)
                return redirect('staff_dashboard')
        messages.error(request, 'Invalid or inactive station staff account.')

    return render(request, 'staff_app/login.html')


def dashboard(request):
    profile = request.user.station_staff_profile
    if not profile.is_active:
        messages.error(request, 'Your station staff account is inactive.')
        return redirect('staff_login')

    station = profile.station
    bookings = Booking.objects.filter(station=station).select_related('user')
    selected_date, date_options = selected_booking_date(request.GET.get('date'))
    slot_rows = build_slot_status_rows(station, selected_date)
    context = {
        'profile': profile,
        'station': station,
        'slot_rows': slot_rows,
        'today_booking_count': bookings.filter(date=timezone.localdate()).count(),
        'active_booking_count': bookings.filter(
            status__in=(Booking.Status.PENDING, Booking.Status.CONFIRMED, Booking.Status.CHARGING),
        ).count(),
        'recent_bookings': bookings[:10],
        'station_status_choices': EVStation.OperationalStatus.choices,
        'slot_status_choices': StationSlotStatus.Status.choices,
        'booking_status_choices': Booking.Status.choices,
        'selected_date': selected_date,
        'date_options': date_options,
    }
    return render(request, 'staff_app/dashboard.html', context)


@require_POST
def update_station_status(request):
    profile = request.user.station_staff_profile
    station = profile.station
    status = request.POST.get('operational_status')
    valid_statuses = {choice for choice, _ in EVStation.OperationalStatus.choices}
    if status not in valid_statuses:
        messages.error(request, 'Select a valid station status.')
        return _dashboard_redirect(request)

    station.operational_status = status
    station.status_message = request.POST.get('status_message', '').strip()[:200]
    station.status_updated_at = timezone.now()
    station.status_updated_by = request.user
    station.save(update_fields=(
        'operational_status', 'status_message', 'status_updated_at', 'status_updated_by',
    ))
    messages.success(request, 'Live station status updated.')
    return _dashboard_redirect(request)


@require_POST
def update_slot_status(request, slot_id):
    profile = request.user.station_staff_profile
    slot = get_object_or_404(chargingslot, pk=slot_id)
    status = request.POST.get('status')
    valid_statuses = {choice for choice, _ in StationSlotStatus.Status.choices}
    if status not in valid_statuses:
        messages.error(request, 'Select a valid slot status.')
        return _dashboard_redirect(request)

    StationSlotStatus.objects.update_or_create(
        station=profile.station,
        slot=slot,
        defaults={
            'status': status,
            'note': request.POST.get('note', '').strip()[:200],
            'updated_by': request.user,
        },
    )
    messages.success(request, f'{slot.slot_name.title()} status updated.')
    return _dashboard_redirect(request)


@require_POST
def update_booking_status(request, booking_id):
    profile = request.user.station_staff_profile
    booking = get_object_or_404(Booking, pk=booking_id, station=profile.station)
    status = request.POST.get('status')
    valid_statuses = {choice for choice, _ in Booking.Status.choices}
    if status not in valid_statuses:
        messages.error(request, 'Select a valid booking status.')
        return _dashboard_redirect(request)

    booking.status = status
    booking.status_updated_at = timezone.now()
    booking.status_updated_by = request.user
    booking.save(update_fields=('status', 'status_updated_at', 'status_updated_by'))
    messages.success(request, f'Booking #{booking.pk} marked {booking.get_status_display()}.')
    return _dashboard_redirect(request)
