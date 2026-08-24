from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from users.models import User
from resources.models import Building, Resource, Booking
import datetime

class ResourceAndBookingAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_superuser(
            email='admin@spu.ac.za',
            password='AdminPassword123!',
            full_name='Admin User'
        )
        self.lecturer = User.objects.create_user(
            email='lecturer@spu.ac.za',
            password='LecturerPassword123!',
            full_name='Dr. Lecturer',
            role='lecturer'
        )
        self.building = Building.objects.create(name='WP Building')
        self.venue = Resource.objects.create(
            name='WP5 (Geo Lab)',
            building=self.building,
            room_number='WP5',
            venue_type='Laboratory',
            capacity=40,
            opening_time=datetime.time(8, 0),
            closing_time=datetime.time(17, 0)
        )

    def test_list_buildings_and_venues(self):
        url = reverse('resources:buildings_list')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(resp.data), 1)

        v_url = reverse('resources:venues_list')
        v_resp = self.client.get(v_url)
        self.assertEqual(v_resp.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(v_resp.data['count'], 1)

    def test_venue_creation_restricted_to_admin(self):
        url = reverse('resources:venues_create')
        data = {
            'name': 'BA01',
            'building': self.building.id,
            'venue_type': 'Classroom',
            'capacity': 50
        }
        self.client.force_authenticate(user=self.lecturer)
        resp = self.client.post(url, data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

        self.client.force_authenticate(user=self.admin)
        resp = self.client.post(url, data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

    def test_booking_creation_and_conflict_detection(self):
        self.client.force_authenticate(user=self.lecturer)
        url = reverse('resources:bookings_list_create')
        data = {
            'resource': self.venue.id,
            'booking_date': '2026-09-01',
            'start_time': '09:00:00',
            'end_time': '11:00:00',
            'purpose': 'NADV744 Lab Test',
            'phone_number': '+27821234567'
        }
        resp = self.client.post(url, data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        booking_id = resp.data['id']

        # Admin approves the booking
        self.client.force_authenticate(user=self.admin)
        status_url = reverse('resources:bookings_status', kwargs={'booking_id': booking_id})
        resp = self.client.patch(status_url, {'status': 'approved'}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        # Overlapping booking attempt
        self.client.force_authenticate(user=self.lecturer)
        conflict_data = {
            'resource': self.venue.id,
            'booking_date': '2026-09-01',
            'start_time': '10:00:00',
            'end_time': '12:00:00',
            'purpose': 'Overlapping Session',
            'phone_number': '+27821234567'
        }
        resp = self.client.post(url, conflict_data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)

    def test_real_availability_endpoint(self):
        url = reverse('resources:venues_availability', kwargs={'resource_id': self.venue.id})
        resp = self.client.get(f'{url}?date=2026-09-01')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn('resource_id', resp.data)

