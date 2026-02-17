from rest_framework.routers import DefaultRouter
from .views import (
    PatientViewSet, DoctorViewSet,
    PharmacyViewSet, MedicalRecordViewSet,
    PrescriptionViewSet,LoginView,LogoutView
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
    path('logout/', LogoutView.as_view(), name='logout'),
] + router.urls