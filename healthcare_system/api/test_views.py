from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.authtoken.models import Token

from core.models import (
    User,
    Patient,
    Doctor,
    Pharmacy,
    MedicalRecord,
    Prescription
)

class TestAuthentication(APITestCase):

    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username="doctor1",
            password="testpass123",
            role="doctor"
        )

    def test_login_success(self):
        """User can login with correct credentials"""

        url = reverse("login")

        response = self.client.post(url, {
            "username": "doctor1",
            "password": "testpass123"
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("token", response.data)

    def test_login_invalid_credentials(self):
        """Login fails with wrong password"""

        url = reverse("login")

        response = self.client.post(url, {
            "username": "doctor1",
            "password": "wrongpassword"
        })

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)



class TestMedicalRecord(APITestCase):

    def setUp(self):

        # Create users
        self.doctor_user = User.objects.create_user(
            username="doc",
            password="pass123",
            role="doctor"
        )

        self.patient_user = User.objects.create_user(
            username="pat",
            password="pass123",
            role="patient"
        )

        # Create profiles
        self.doctor = Doctor.objects.create(
            user=self.doctor_user,
            specialization="Cardiology",
            license_number="12345"
        )

        self.patient = Patient.objects.create(
            user=self.patient_user,
            full_name="John Doe",
            date_of_birth="1990-01-01",
            gender="Male",
            phone_number="1234567890",
            address="Accra"
        )

        # Create medical record
        self.record = MedicalRecord.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            diagnosis="Malaria",
            treatment="Medication",
            notes="Stable"
        )

        # Create tokens
        self.doctor_token = Token.objects.create(user=self.doctor_user)
        self.patient_token = Token.objects.create(user=self.patient_user)

    def test_doctor_can_view_records(self):
        """Doctor should see all medical records"""

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Token {self.doctor_token.key}"
        )

        response = self.client.get("/api/medical-records/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_patient_can_only_see_own_records(self):
        """Patient should only see their own record"""

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Token {self.patient_token.key}"
        )

        response = self.client.get("/api/medical-records/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)


    def test_filter_medical_record_by_patient(self):
        """Filtering medical records by patient ID"""

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Token {self.doctor_token.key}"
        )

        response = self.client.get(
            f"/api/medical-records/?patient={self.patient.id}"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)


class TestPrescription(APITestCase):

    def setUp(self):

        self.pharmacist_user = User.objects.create_user(
            username="pharma",
            password="pass123",
            role="pharmacist"
        )

        self.pharmacist_token = Token.objects.create(
            user=self.pharmacist_user
        )

    def test_pharmacist_can_view_prescriptions(self):
        """Pharmacist should be able to view prescriptions"""

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Token {self.pharmacist_token.key}"
        )

        response = self.client.get("/api/prescriptions/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthorized_access_denied(self):
        """Access without token should fail"""

        response = self.client.get("/api/prescriptions/")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class TestLogout(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="logoutuser",
            password="pass123",
            role="doctor"
        )

        self.token = Token.objects.create(user=self.user)

    def test_logout_deletes_token(self):
        """Logout should delete user token"""

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Token {self.token.key}"
        )

        response = self.client.post(reverse("logout"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Token should no longer exist
        self.assertFalse(
            Token.objects.filter(user=self.user).exists()
        )      