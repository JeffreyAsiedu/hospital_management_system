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


# Create your views here.
class PatientViewSet(ModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    permission_classes = [IsAuthenticated]


class DoctorViewSet(ModelViewSet):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer
    permission_classes = [IsAuthenticated]


class PharmacyViewSet(ModelViewSet):
    queryset = Pharmacy.objects.all()
    serializer_class = PharmacySerializer
    permission_classes = [IsAuthenticated]    


class MedicalRecordViewSet(ModelViewSet):
    queryset = MedicalRecord.objects.all()
    serializer_class = MedicalRecordSerializer
    permission_classes = [IsAuthenticated, IsDoctor] 


class PrescriptionViewSet(ModelViewSet):
    queryset = Prescription.objects.all()
    serializer_class = PrescriptionSerializer
    permission_classes = [IsAuthenticated]   



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