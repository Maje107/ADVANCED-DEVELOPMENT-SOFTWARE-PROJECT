from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from users.models import User

class UserAuthAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = User.objects.create_superuser(
            email='admin@spu.ac.za',
            password='AdminPassword123!',
            full_name='System Administrator'
        )
        self.lecturer = User.objects.create_user(
            email='lecturer@spu.ac.za',
            password='LecturerPassword123!',
            full_name='Dr. Smith',
            role='lecturer'
        )

    def test_lecturer_registration_success(self):
        url = reverse('users:register')
        data = {
            'email': 'newlecturer@spu.ac.za',
            'full_name': 'Prof. Johnson',
            'role': 'lecturer',
            'password': 'StrongPassword123!',
            'password_confirm': 'StrongPassword123!',
            'phone_number': '+27821112233'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email='newlecturer@spu.ac.za').exists())

    def test_student_leader_registration_success(self):
        url = reverse('users:register')
        data = {
            'email': 'leader@spu.ac.za',
            'full_name': 'Sarah Student',
            'role': 'student_leader',
            'leadership_role': 'peer_mentor',
            'student_number': '20230005',
            'password': 'StrongPassword123!',
            'password_confirm': 'StrongPassword123!',
            'phone_number': '+27829998877'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email='leader@spu.ac.za').exists())

    def test_password_mismatch_fails(self):
        url = reverse('users:register')
        data = {
            'email': 'mismatch@spu.ac.za',
            'full_name': 'Mismatch Test',
            'role': 'lecturer',
            'password': 'Password123!',
            'password_confirm': 'WrongPassword123!',
            'phone_number': '+27821112233'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)

    def test_admin_registration_prevented(self):
        url = reverse('users:register')
        data = {
            'email': 'fakeadmin@spu.ac.za',
            'full_name': 'Fake Admin',
            'role': 'admin',
            'password': 'Password123!',
            'password_confirm': 'Password123!',
            'phone_number': '+27821112233'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)

    def test_forgot_and_reset_password_flow(self):
        forgot_url = reverse('users:forgot_password')
        resp = self.client.post(forgot_url, {'email': 'lecturer@spu.ac.za'}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        reset_token = resp.data['reset_token']

        reset_url = reverse('users:reset_password')
        reset_data = {
            'email': 'lecturer@spu.ac.za',
            'reset_token': reset_token,
            'new_password': 'BrandNewPassword123!',
            'confirm_password': 'BrandNewPassword123!'
        }
        reset_resp = self.client.post(reset_url, reset_data, format='json')
        self.assertEqual(reset_resp.status_code, status.HTTP_200_OK)

        login_url = reverse('users:login')
        login_resp = self.client.post(login_url, {'email': 'lecturer@spu.ac.za', 'password': 'BrandNewPassword123!'}, format='json')
        self.assertEqual(login_resp.status_code, status.HTTP_200_OK)
        self.assertIn('access_token', login_resp.data)

