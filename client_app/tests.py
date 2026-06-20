import datetime
import json
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from home.models import OwnerProfile, UserProfile
from owner_app.models import EVStation, chargingslot
from staff_app.models import StationSlotStatus

from .models import Booking

class ClientBookingOperationsTests(TestCase):
    def setUp(self):
        owner_user = User.objects.create_user('booking-owner', password='OwnerPass123!')
        owner = OwnerProfile.objects.create(
            user=owner_user, owner_name='Owner', phone='9999999999',
        )
        self.station = EVStation.objects.create(
            owner=owner,
            station_name='Bookable Station',
            city='Kochi',
            station_type='Fast Charging',
            total_slots=2,
            rate_per_unit='20.00',
            phone_number='9999999999',
            is_active=True,
            operational_status=EVStation.OperationalStatus.OPEN,
        )
        self.slot, _ = chargingslot.objects.update_or_create(
            slot_id=201,
            defaults={
                'slot_name': 'Slot 1',
                'start_time': '06:00 AM',
                'end_time': '07:00 AM',
            },
        )
        self.user = User.objects.create_user('driver', password='DriverPass123!')
        UserProfile.objects.create(user=self.user, name='Driver', phone='8888888888')
        self.client.force_login(self.user)

    def booking_payload(self):
        return {
            'selected_date': (timezone.localdate() + datetime.timedelta(days=1)).isoformat(),
            'selected_slot': 'Slot 1',
            'selected_start': 'TAMPERED',
            'selected_end': 'TAMPERED',
        }

    def test_client_cannot_book_operationally_unavailable_slot(self):
        StationSlotStatus.objects.create(
            station=self.station,
            slot=self.slot,
            status=StationSlotStatus.Status.MAINTENANCE,
        )
        self.client.post(reverse('book_now', args=[self.station.pk]), self.booking_payload())
        self.assertFalse(Booking.objects.exists())

    def test_booking_uses_server_side_slot_times(self):
        self.assertEqual(self.client.get(reverse('station_search')).status_code, 200)
        self.assertEqual(self.client.get(reverse('book_now', args=[self.station.pk])).status_code, 200)
        self.client.post(reverse('book_now', args=[self.station.pk]), self.booking_payload())
        booking = Booking.objects.get()
        self.assertEqual(booking.start_time, '06:00 AM')
        self.assertEqual(booking.end_time, '07:00 AM')
        self.assertEqual(booking.status, Booking.Status.PENDING)

    def test_closed_station_rejects_booking(self):
        self.station.operational_status = EVStation.OperationalStatus.CLOSED
        self.station.save(update_fields=('operational_status',))
        self.client.post(reverse('book_now', args=[self.station.pk]), self.booking_payload())
        self.assertFalse(Booking.objects.exists())

    def test_cancelled_booking_releases_unique_slot(self):
        booking = Booking.objects.create(
            user=self.user,
            station=self.station,
            date=datetime.date.today(),
            slot_name='Slot 1',
            start_time='06:00 AM',
            end_time='07:00 AM',
            status=Booking.Status.CANCELLED,
        )
        self.assertEqual(booking.status, Booking.Status.CANCELLED)
        self.client.post(reverse('book_now', args=[self.station.pk]), self.booking_payload())
        self.assertEqual(Booking.objects.count(), 2)

    @patch('client_app.views.timezone.localdate')
    @patch('client_app.views.timezone.localtime')
    def test_past_slots_are_hidden_for_today(self, mock_localtime, mock_localdate):
        mock_localdate.return_value = datetime.date(2026, 6, 20)
        mock_localtime.return_value = timezone.make_aware(
            datetime.datetime(2026, 6, 20, 7, 5),
            timezone.get_current_timezone(),
        )

        response = self.client.get(reverse('book_now', args=[self.station.pk]))
        slot_data = json.loads(response.context['slots_json'])

        self.assertEqual(slot_data[0][0]['time'], '07:00 AM - 08:00 AM')
        self.assertNotIn('06:00 AM - 07:00 AM', [slot['time'] for slot in slot_data[0]])

    @patch('client_app.views.timezone.localdate')
    @patch('client_app.views.timezone.localtime')
    def test_past_slot_cannot_be_booked_after_end_time(self, mock_localtime, mock_localdate):
        mock_localdate.return_value = datetime.date(2026, 6, 20)
        mock_localtime.return_value = timezone.make_aware(
            datetime.datetime(2026, 6, 20, 7, 5),
            timezone.get_current_timezone(),
        )

        self.client.post(
            reverse('book_now', args=[self.station.pk]),
            {
                'selected_date': '2026-06-20',
                'selected_slot': 'Slot 1',
                'selected_start': '06:00 AM',
                'selected_end': '07:00 AM',
            },
        )

        self.assertFalse(Booking.objects.exists())
