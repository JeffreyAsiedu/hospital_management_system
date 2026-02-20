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
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter


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
    
    def perform_create(self, serializer):
        #Only admin can create patients
        if self.request.user.role != "admin":
            raise PermissionDenied("Only admin can create patients.")
        serializer.save()

    def perform_update(self, serializer):
        user = self.request.user

        #Patients can update their own profile
        if user.role == "patient":
            serializer.save(user=user) 
            return

        #Admin can update anyone
        if user.role == "admin":
            serializer.save()
            return

        raise PermissionDenied("You cannot update")   
    
    def destroy(self, request, *args, **kwargs):
        #Prevent doctors from deleting patients
        if request.user.role == "doctor":
            raise PermissionDenied("Doctors cannot delete patients.")
        return super().destroy(request, *args, **kwargs)

class DoctorViewSet(ModelViewSet):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.role == "admin":
            return Doctor.objects.all()
        
        if user.role == "doctor":
            return Doctor.objects.filter(user=user)
        
        return Doctor.objects.none()
    
    def perform_create(self, serializer):
        #Only admin can create doctors
        if self.request.user.role != "admin":
            raise PermissionDenied("Only admin can create doctors.")
        serializer.save()

    def perform_update(self, serializer):
        user = self.request.user

        #Doctors can update their own profile
        if user.role == "doctor":
            serializer.save(user=user) 
            return

        #Admin can update anyone
        if user.role == "admin":
            serializer.save()
            return

        raise PermissionDenied("You cannot update")
    

class PharmacyViewSet(ModelViewSet):
    queryset = Pharmacy.objects.all()
    serializer_class = PharmacySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.role == "pharmacist":
            return Prescription.objects.all()

        if user.role == "doctor":
            return Prescription.objects.filter(doctor__user=user)

        if user.role == "patient":
            return Prescription.objects.filter(patient__user=user)   

        return Prescription.objects.none()
    
    def perform_create(self, serializer):
        #Only admin can add pharmacies
        if self.request.user.role != "admin":
            raise PermissionDenied("Only admin can create pharmacies.")
        serializer.save()


class MedicalRecordViewSet(ModelViewSet):
    """Controls access to medical records"""
    queryset = MedicalRecord.objects.all()
    serializer_class = MedicalRecordSerializer
    permission_classes = [IsAuthenticated]
    
    #Enable filter backends
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]

    #Exact Field filtering 
    filterset_fields = ['patient', 'doctor']

    #Text search fields
    search_fields = ['diagnosis', 'treatment', 'notes']

    #Allow ordering
    ordering_fields = ['date_created', 'last_updated']

    def get_queryset(self):
        user = self.request.user

        if user.role == "doctor":
            return MedicalRecord.objects.all()
        
        if user.role == "patient":
            return MedicalRecord.objects.filter(patient__user=user)

        return MedicalRecord.objects.none()
    
    def perform_create(self, serializer):
        #Only doctors can create medical records
        if self.request.user.role != "doctor":
            raise PermissionDenied("Only doctors can create medical records.")
        serializer.save()

    def perform_update(self, serializer):
        #Only doctors can update medical records
        if self.request.user.role != "doctor":
            raise PermissionDenied("Only doctors can update medical records.")
        serializer.save()


class PrescriptionViewSet(ModelViewSet):
    """Controls access to medical records"""
    queryset = Prescription.objects.all()
    serializer_class = PrescriptionSerializer
    permission_classes = [IsAuthenticated] 

    #Enable filter backends
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]

    #Exact Field filtering 
    filterset_fields = ['patient', 'doctor', 'pharmacy']

    #Text search fields
    search_fields = ['medication_name', 'instructions']

    #Allow ordering
    ordering_fields = ['issue_date']

    def get_queryset(self):
        user = self.request.user

        if user.role == "doctor":
            return Prescription.objects.filter(doctor__user =user)
        
        if user.role == "patient":
            return Prescription.objects.filter(patient__user=user)
        
        if user.role == "pharmacist":
            return Prescription.objects.all()

        return Prescription.objects.none()
    
    def perform_create(self, serializer):
        if self.request.user.role != "doctor":
            raise PermissionDenied("Only doctors can create prescriptions.")
        serializer.save()

    def perform_update(self, serializer):
        #Only doctors can update prescriptions
        if self.request.user.role != "doctor":
            raise PermissionDenied("Only doctors can update prescriptions.")
        serializer.save()

    def destroy(self, request, *args, **kwargs):
        #Prevent pharmacists from deleting
        if request.user.role == "pharmacist":
            raise PermissionDenied("Pharmacists cannot delete prescriptions.")
        return super().destroy(request, *args, **kwargs)
    


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