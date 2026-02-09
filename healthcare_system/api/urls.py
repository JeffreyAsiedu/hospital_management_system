from rest_framework.routers import DefaultRouter
from .views import (
    PatientViewSet, DoctorViewSet,
    PharmacyViewSet, MedicalRecordViewSet,
    PrescriptionViewSet
)

router = DefaultRouter()
router.register('patients', PatientViewSet)
router.register('doctors', DoctorViewSet)
router.register('pharmacies', PharmacyViewSet)
router.register('medical-records', MedicalRecordViewSet)
router.register('prescriptions', PrescriptionViewSet)

urlpatterns = router.urls