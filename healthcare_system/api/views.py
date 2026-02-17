from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from core.models import Patient, Doctor, Pharmacy, MedicalRecord, Prescription
from .serializers import PatientSerializer, DoctorSerializer, PharmacySerializer, MedicalRecordSerializer, PrescriptionSerializer
from .permissions import IsDoctor
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework.exceptions import PermissionDenied


# Create your views here.
class PatientViewSet(ModelViewSet):
    """Controls access to patient records"""
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.role == "admin":
            return Patient.objects.all()
        
        if user.role == "doctor":
            return Patient.objects.all()
        
        if user.role == "patient":
            return Patient.objects.filter(user=user)
        
        return Patient.objects.none()
    
    def destroy(self, request, *args, **kwargs):
        #Prevent doctors from deleting patients
        if request.user.role == "doctor":
            raise PermissionDenied("Doctors cannot delete patients.")
        return super().destroy(request, *args, **kwargs)

class DoctorViewSet(ModelViewSet):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer
    permission_classes = [IsAuthenticated]


class PharmacyViewSet(ModelViewSet):
    queryset = Pharmacy.objects.all()
    serializer_class = PharmacySerializer
    permission_classes = [IsAuthenticated]    


class MedicalRecordViewSet(ModelViewSet):
    """Controls access to medical records"""
    queryset = MedicalRecord.objects.all()
    serializer_class = MedicalRecordSerializer
    permission_classes = [IsAuthenticated, IsDoctor]

    def get_queryset(self):
        user = self.request.user

        if user.role == "doctor":
            return MedicalRecord.objects.all()

        if user.role == "patient":
            return MedicalRecord.objects.filter(patient__user=user)

        return MedicalRecord.objects.none()


class PrescriptionViewSet(ModelViewSet):
    """Controls access to medical records"""
    queryset = Prescription.objects.all()
    serializer_class = PrescriptionSerializer
    permission_classes = [IsAuthenticated] 

    def get_queryset(self):
        user = self.request.user

        if user.role == "doctor":
            return Prescription.objects.filter(doctor__user=user)
        
        if user.role == "patient":
            return Prescription.objects.filter(patient__user=user)

        if user.role == "pharmacist":
            return Prescription.objects.all()
        
        return Prescription.objects.none()
    

    def destroy(self, request, *args, **kwargs):
        #Prevent pharmacists from deleting
        if request.user.role == "pharmacist":
            raise PermissionDenied("Pharmacists cannot delete prescriptions.")
        return super().destroy(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        #Prevent pharmacists from updating
        if request.user.role == "pharmacist":
            raise PermissionDenied("Pharmacists cannot update prescriptions.")
        return super().update(request, *args, **kwargs)


class LoginView(APIView):
     #Allow anyone to access login(even unauthenticated users)
    permission_classes = []

    #Extract username and password from request body
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        #Authenticate checks if credentials are valid
        user = authenticate(username=username, password=password)

        if user is None:
            return Response(
                {"error": "Invalid credentials"},
                status=status.HTTP_401_UNAUTHORIZED 
            )
        
        #Get existing token or create one if it doesn't exist
        token, created = Token.objects.get_or_create(user=user)

        return Response({
            "token": token.key,
            "user_id": user.id,
            "role": user.role,
            "username": user.username
        })
    

class LogoutView(APIView):
    """Logs out user by deleting their authentication token."""
    
    permission_classes = [IsAuthenticated]

    def post(self, request):
        #Delete the user's token
        request.user.auth_token.delete()

        return Response({"message": "Successfully logged out."})