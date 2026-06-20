import datetime

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from client_app.models import Booking
from home.models import OwnerProfile, UserProfile
from owner_app.models import EVStation, chargingslot

from .models import StationSlotStatus, StationStaffProfile


class StationStaffOperationsTests(TestCase):
    def setUp(self):
        self.owner_user = User.objects.create_user('owner', password='OwnerPass123!')
        self.owner = OwnerProfile.objects.create(
            user=self.owner_user,
            owner_name='Station Owner',
            phone='9999999999',
        )
        self.station = EVStation.objects.create(
            owner=self.owner,
            station_name='Central Charge',
            city='Kochi',
            station_type='Fast Charging',
            total_slots=4,
            rate_per_unit='18.00',
            phone_number='9999999999',
            is_active=True,
        )
        self.staff_user = User.objects.create_user('operator', password='StaffPass123!')
        self.staff = StationStaffProfile.objects.create(
            user=self.staff_user,
            station=self.station,
            created_by=self.owner,
            full_name='Station Operator',
            phone='8888888888',
            employee_id='EMP-01',
        )
        self.slot, _ = chargingslot.objects.update_or_create(
            slot_id=201,
            defaults={
                'slot_name': 'Slot 1',
                'start_time': '06:00 AM',
                'end_time': '07:00 AM',
            },
        )

    def test_staff_login_rejects_an_owner_account(self):
        response = self.client.post(reverse('staff_login'), {
            'username': 'owner',
            'password': 'OwnerPass123!',
        })
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_staff_updates_its_station_and_slot(self):
        self.client.force_login(self.staff_user)
        dashboard = self.client.get(reverse('staff_dashboard'))
        self.assertEqual(dashboard.status_code, 200)
        self.assertContains(dashboard, 'Central Charge')
        response = self.client.post(reverse('update_station_status'), {
            'operational_status': EVStation.OperationalStatus.OPEN,
            'status_message': 'All chargers ready',
        })
        self.assertRedirects(response, reverse('staff_dashboard'))
        self.station.refresh_from_db()
        self.assertEqual(self.station.operational_status, EVStation.OperationalStatus.OPEN)
        self.assertEqual(self.station.status_updated_by, self.staff_user)

        self.client.post(reverse('update_slot_status', args=[self.slot.pk]), {
            'status': StationSlotStatus.Status.MAINTENANCE,
            'note': 'Cable inspection',
        })
        slot_status = StationSlotStatus.objects.get(station=self.station, slot=self.slot)
        self.assertEqual(slot_status.status, StationSlotStatus.Status.MAINTENANCE)
        self.assertEqual(slot_status.updated_by, self.staff_user)

    def test_staff_cannot_update_another_stations_booking(self):
        other_station = EVStation.objects.create(
            owner=self.owner,
            station_name='Other Charge',
            city='Kochi',
            station_type='Fast Charging',
            total_slots=2,
            rate_per_unit='15.00',
            phone_number='7777777777',
            is_active=True,
        )
        client_user = User.objects.create_user('driver', password='DriverPass123!')
        UserProfile.objects.create(user=client_user, name='Driver', phone='7777777777')
        booking = Booking.objects.create(
            user=client_user,
            station=other_station,
            date=datetime.date.today(),
            slot_name='Slot 1',
            start_time='06:00 AM',
            end_time='07:00 AM',
        )
        self.client.force_login(self.staff_user)
        response = self.client.post(reverse('update_booking_status', args=[booking.pk]), {
            'status': Booking.Status.CONFIRMED,
        })
        self.assertEqual(response.status_code, 404)
        booking.refresh_from_db()
        self.assertEqual(booking.status, Booking.Status.PENDING)

    def test_staff_sees_combined_slot_status_and_keeps_selected_date(self):
        selected_date = timezone.localdate() + datetime.timedelta(days=1)
        client_user = User.objects.create_user('scheduled-driver', password='DriverPass123!')
        UserProfile.objects.create(user=client_user, name='Scheduled Driver', phone='7777777777')
        booking = Booking.objects.create(
            user=client_user,
            station=self.station,
            date=selected_date,
            slot_name=self.slot.slot_name,
            start_time=self.slot.start_time,
            end_time=self.slot.end_time,
        )
        StationSlotStatus.objects.create(
            station=self.station,
            slot=self.slot,
            status=StationSlotStatus.Status.MAINTENANCE,
            note='Cable inspection',
        )

        self.client.force_login(self.staff_user)
        dashboard_url = f'{reverse("staff_dashboard")}?date={selected_date.isoformat()}'
        response = self.client.get(dashboard_url)
        row = next(row for row in response.context['slot_rows'] if row['slot'] == self.slot)
        self.assertEqual(row['condition_label'], 'Maintenance')
        self.assertEqual(row['booking_label'], 'Booking pending')
        self.assertEqual(row['booking'], booking)
        self.assertContains(response, 'scheduled-driver')

        response = self.client.post(reverse('update_booking_status', args=[booking.pk]), {
            'status': Booking.Status.CANCELLED,
            'selected_date': selected_date.isoformat(),
        })
        self.assertRedirects(response, dashboard_url)
        booking.refresh_from_db()
        self.assertEqual(booking.status, Booking.Status.CANCELLED)

        response = self.client.get(dashboard_url)
        row = next(row for row in response.context['slot_rows'] if row['slot'] == self.slot)
        self.assertIsNone(row['booking'])
        self.assertEqual(row['booking_label'], 'Available')
        self.assertEqual(row['condition_label'], 'Maintenance')


class OwnerStaffManagementTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('owner2', password='OwnerPass123!')
        self.owner = OwnerProfile.objects.create(
            user=self.user,
            owner_name='Owner Two',
            phone='9999999999',
        )
        self.station = EVStation.objects.create(
            owner=self.owner,
            station_name='Owner Two Station',
            city='Thrissur',
            station_type='Normal Charging',
            total_slots=2,
            rate_per_unit='12.00',
            phone_number='9999999999',
        )

    def test_owner_can_create_and_deactivate_staff_account(self):
        self.client.force_login(self.user)
        self.assertEqual(self.client.get(reverse('owner_dashboard')).status_code, 200)
        self.assertEqual(self.client.get(reverse('manage_staff')).status_code, 200)
        self.assertEqual(self.client.get(reverse('add_staff')).status_code, 200)
        response = self.client.post(reverse('add_staff'), {
            'station': self.station.pk,
            'full_name': 'New Operator',
            'employee_id': 'OPS-9',
            'phone': '8888888888',
            'email': 'operator@example.com',
            'username': 'newoperator',
            'password': 'SafeStaffPass123!',
            'confirm_password': 'SafeStaffPass123!',
        })
        self.assertRedirects(response, reverse('manage_staff'))
        profile = StationStaffProfile.objects.get(user__username='newoperator')
        self.assertEqual(profile.station, self.station)
        self.assertEqual(profile.created_by, self.owner)

        self.client.post(reverse('toggle_staff', args=[profile.pk]))
        profile.refresh_from_db()
        profile.user.refresh_from_db()
        self.assertFalse(profile.is_active)
        self.assertFalse(profile.user.is_active)

    def test_owner_sees_owned_station_slot_status_but_not_other_stations(self):
        selected_date = timezone.localdate() + datetime.timedelta(days=2)
        slot, _ = chargingslot.objects.update_or_create(
            slot_id=201,
            defaults={
                'slot_name': 'Slot 1',
                'start_time': '06:00 AM',
                'end_time': '07:00 AM',
            },
        )
        driver = User.objects.create_user('owner-view-driver', password='DriverPass123!')
        UserProfile.objects.create(user=driver, name='Owner View Driver', phone='7777777777')
        booking = Booking.objects.create(
            user=driver,
            station=self.station,
            date=selected_date,
            slot_name=slot.slot_name,
            start_time=slot.start_time,
            end_time=slot.end_time,
            status=Booking.Status.CONFIRMED,
        )
        StationSlotStatus.objects.create(
            station=self.station,
            slot=slot,
            status=StationSlotStatus.Status.UNAVAILABLE,
            note='Connector fault',
        )

        self.client.force_login(self.user)
        dashboard_url = (
            f'{reverse("owner_dashboard")}?station={self.station.pk}'
            f'&date={selected_date.isoformat()}'
        )
        response = self.client.get(dashboard_url)
        row = next(row for row in response.context['slot_rows'] if row['slot'] == slot)
        self.assertEqual(row['condition_label'], 'Unavailable')
        self.assertEqual(row['booking_label'], 'Booked / Confirmed')
        self.assertEqual(row['booking'], booking)
        self.assertContains(response, 'owner-view-driver')
        self.assertContains(response, 'Connector fault')

        other_user = User.objects.create_user('other-owner', password='OwnerPass123!')
        other_owner = OwnerProfile.objects.create(
            user=other_user,
            owner_name='Other Owner',
            phone='6666666666',
        )
        other_station = EVStation.objects.create(
            owner=other_owner,
            station_name='Private Station',
            city='Kochi',
            station_type='Fast Charging',
            total_slots=2,
            rate_per_unit='15.00',
            phone_number='6666666666',
        )
        forbidden_response = self.client.get(
            reverse('owner_dashboard'),
            {'station': other_station.pk, 'date': selected_date.isoformat()},
        )
        self.assertEqual(forbidden_response.status_code, 404)
        malformed_response = self.client.get(reverse('owner_dashboard'), {'station': 'invalid'})
        self.assertEqual(malformed_response.status_code, 404)
