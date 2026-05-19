from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated

from api.models import CustomUser, Doctor, Patient, PatientDoctorMapping
from api.serializers import (
    UserRegisterSerializer,
    LoginSerializer,
    DoctorSerializer,
    PatientSerializer,
    MappingSerializer,
)


class UserRegisterView(APIView):
    """
    POST only.
    Registers a new system operator CustomUser.
    Returns standard JWT access token on success.
    """
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = UserRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        from rest_framework_simplejwt.tokens import RefreshToken
        token = str(RefreshToken.for_user(user).access_token)
        
        return Response({
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": "admin",
            "token": token
        }, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    """
    POST only.
    Logs in the system operator using email & password.
    Returns JWT access and refresh tokens.
    """
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class DoctorListCreateView(APIView):
    """
    GET: List all doctors.
    POST: Register a new standalone doctor entry.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        doctors = Doctor.objects.all()
        serializer = DoctorSerializer(doctors, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        serializer = DoctorSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class DoctorDetailView(APIView):
    """
    GET: Retrieve doctor details.
    PUT: Update doctor record.
    DELETE: Remove doctor record.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, pk, *args, **kwargs):
        doctor = get_object_or_404(Doctor, pk=pk)
        serializer = DoctorSerializer(doctor)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk, *args, **kwargs):
        doctor = get_object_or_404(Doctor, pk=pk)
        serializer = DoctorSerializer(doctor, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk, *args, **kwargs):
        doctor = get_object_or_404(Doctor, pk=pk)
        doctor.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PatientListCreateView(APIView):
    """
    GET: List patients created by the authenticated operator.
    POST: Create a new standalone patient record linked to the operator.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        patients = Patient.objects.filter(created_by=request.user)
        serializer = PatientSerializer(patients, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        serializer = PatientSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(created_by=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class PatientDetailView(APIView):
    """
    GET: Retrieve patient details (must be created by request.user).
    PUT: Update patient details.
    DELETE: Delete patient record.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, pk, *args, **kwargs):
        patient = get_object_or_404(Patient, pk=pk, created_by=request.user)
        serializer = PatientSerializer(patient)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk, *args, **kwargs):
        patient = get_object_or_404(Patient, pk=pk, created_by=request.user)
        serializer = PatientSerializer(patient, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk, *args, **kwargs):
        patient = get_object_or_404(Patient, pk=pk, created_by=request.user)
        patient.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class MappingListCreateView(APIView):
    """
    GET: List doctor-patient assignments created by the authenticated operator.
    POST: Assign a doctor to a patient owned by the operator.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        mappings = PatientDoctorMapping.objects.filter(patient__created_by=request.user)
        serializer = MappingSerializer(mappings, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        serializer = MappingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        patient = serializer.validated_data['patient']
        if patient.created_by != request.user:
            return Response(
                {"error": "You do not have permission to assign doctors to this patient."},
                status=status.HTTP_403_FORBIDDEN
            )
            
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class MappingPatientDetailView(APIView):
    """
    GET: Retrieve list of Doctors assigned to a specific patient.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, patient_id, *args, **kwargs):
        patient = get_object_or_404(Patient, pk=patient_id, created_by=request.user)
        mappings = PatientDoctorMapping.objects.filter(patient=patient)
        doctors = [m.doctor for m in mappings]
        serializer = DoctorSerializer(doctors, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class MappingDeleteView(APIView):
    """
    DELETE: Dismiss a specific doctor-patient care relationship.
    """
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk, *args, **kwargs):
        mapping = get_object_or_404(PatientDoctorMapping, pk=pk, patient__created_by=request.user)
        mapping.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
