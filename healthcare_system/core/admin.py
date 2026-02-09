from django.contrib import admin
from .models import User, Patient, Doctor, Pharmacy, MedicalRecord, Prescription

# Register your models here.
admin.site.register(User)
admin.site.register(Patient)
admin.site.register(Doctor)
admin.site.register(Pharmacy)
admin.site.register(MedicalRecord)
admin.site.register(Prescription)