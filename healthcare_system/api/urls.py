from rest_framework.routers import DefaultRouter
from .views import (
    PatientViewSet, DoctorViewSet,
    PharmacyViewSet, MedicalRecordViewSet,
    PrescriptionViewSet,LoginView
)
from django.urls import path

router = DefaultRouter()
router.register('patients', PatientViewSet)
router.register('doctors', DoctorViewSet)
router.register('pharmacies', PharmacyViewSet)
router.register('medical-records', MedicalRecordViewSet)
router.register('prescriptions', PrescriptionViewSet)


urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
] + router.urls