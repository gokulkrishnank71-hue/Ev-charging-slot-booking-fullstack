from django.contrib import messages
from django.http import Http404
from django.shortcuts import get_object_or_404, render, redirect
from django.views.decorators.http import require_POST
from django.utils import timezone
from .models import EVStation
from home.models import OwnerProfile
from home.decorators import owner_required
from client_app.models import Booking
from staff_app.models import StationStaffProfile
from staff_app.slot_status import build_slot_status_rows, selected_booking_date
from .forms import StationStaffCreateForm

# ==================================================
# EV Point - Owner Module Views
# Handles owner dashboard and charging station management
# ==================================================

# ==================================================
# Owner Dashboard View
# Displays dashboard for authenticated station owners
# ==================================================
@owner_required
def owner_dashboard(request):

    # Allow access only to logged-in owners
    if not request.user.is_authenticated:

        return redirect('owner_login')

    owner = request.user.ownerprofile
    stations = EVStation.objects.filter(owner=owner)
    bookings = Booking.objects.filter(station__owner=owner).select_related('user', 'station')
    selected_station = None
    selected_station_id = request.GET.get('station')
    if selected_station_id:
        if not selected_station_id.isdigit():
            raise Http404('Station not found.')
        selected_station = get_object_or_404(stations, pk=selected_station_id)
    else:
        selected_station = stations.first()

    selected_date, date_options = selected_booking_date(request.GET.get('date'))
    slot_rows = (
        build_slot_status_rows(selected_station, selected_date)
        if selected_station else []
    )
    return render(
        request,
        'owner_app/owner_dashboard.html',
        {
            'stations': stations,
            'station_count': stations.count(),
            'staff_count': StationStaffProfile.objects.filter(created_by=owner, is_active=True).count(),
            'today_booking_count': bookings.filter(date=timezone.localdate()).count(),
            'recent_bookings': bookings[:8],
            'selected_station': selected_station,
            'selected_date': selected_date,
            'date_options': date_options,
            'slot_rows': slot_rows,
        },
    )

# ==================================================
# Add Station View
# Creates a new EV charging station for the owner
# ==================================================
@owner_required
def add_station(request):

    # Process station registration form submission
    if request.method == "POST":

        # Retrieve logged-in owner's profile
        owner = OwnerProfile.objects.get(user=request.user)

        # Collect station details from submitted form
        station_name = request.POST.get('station_name')
        city = request.POST.get('city')
        station_type = request.POST.get('station_type')
        total_slots = request.POST.get('total_slots')
        rate_per_unit = request.POST.get('rate_per_unit')
        phone_number = request.POST.get('phone_number')

        # Create and save EV station record
        EVStation.objects.create(
            owner=owner,
            station_name=station_name,
            city=city,
            station_type=station_type,
            total_slots=total_slots,
            rate_per_unit=rate_per_unit,
            phone_number=phone_number
        )

        # Redirect to dashboard after successful creation
        return redirect('owner_dashboard')

    # Display add station form page
    return render(request, 'owner_app/add_station.html')


@owner_required
def manage_staff(request):
    owner = request.user.ownerprofile
    staff_members = StationStaffProfile.objects.filter(
        created_by=owner,
    ).select_related('user', 'station')
    return render(request, 'owner_app/manage_staff.html', {'staff_members': staff_members})


@owner_required
def add_staff(request):
    owner = request.user.ownerprofile
    if request.method == 'POST':
        form = StationStaffCreateForm(request.POST, owner=owner)
        if form.is_valid():
            staff = form.save()
            messages.success(request, f'Staff account for {staff.full_name} was created successfully.')
            return redirect('manage_staff')
    else:
        form = StationStaffCreateForm(owner=owner)
    return render(request, 'owner_app/add_staff.html', {'form': form})


@require_POST
@owner_required
def toggle_staff(request, staff_id):
    owner = request.user.ownerprofile
    staff = get_object_or_404(StationStaffProfile, pk=staff_id, created_by=owner)
    staff.is_active = not staff.is_active
    staff.user.is_active = staff.is_active
    staff.save(update_fields=('is_active',))
    staff.user.save(update_fields=('is_active',))
    state = 'activated' if staff.is_active else 'deactivated'
    messages.success(request, f'{staff.full_name} was {state}.')
    return redirect('manage_staff')
