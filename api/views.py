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


class DoctorRegisterView(APIView):
    """
    POST only.
    Registers a new Doctor profile and corresponding CustomUser.
    Returns standard JWT access token on success.
    """
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = DoctorSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        doctor = serializer.save()

        from rest_framework_simplejwt.tokens import RefreshToken
        token = str(RefreshToken.for_user(doctor.user).access_token)

        return Response({
            "id": doctor.user.id,
            "name": doctor.user.name,
            "email": doctor.user.email,
            "role": "doctor",
            "token": token
        }, status=status.HTTP_201_CREATED)


class PatientRegisterView(APIView):
    """
    POST only.
    Registers a new Patient profile and corresponding CustomUser.
    Returns standard JWT access token on success.
    """
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = PatientSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Set default created_by to the first admin operator user (non-nullable relationship)
        admin_user = CustomUser.objects.filter(role='admin').first()
        if not admin_user:
            admin_user = CustomUser.objects.filter(is_superuser=True).first()

        patient = serializer.save(created_by=admin_user)

        from rest_framework_simplejwt.tokens import RefreshToken
        token = str(RefreshToken.for_user(patient.user).access_token)

        return Response({
            "id": patient.user.id,
            "name": patient.user.name,
            "email": patient.user.email,
            "role": "patient",
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
        if request.user.role != 'admin':
            return Response({"error": "Only administrators can register doctors."}, status=status.HTTP_403_FORBIDDEN)
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
        # Allow if user is admin, or if the user is the doctor updating their own profile
        is_self = False
        try:
            if hasattr(request.user, 'doctor_profile') and request.user.doctor_profile.id == pk:
                is_self = True
            elif request.user.id == pk:
                is_self = True
        except Exception:
            pass

        if request.user.role != 'admin' and not is_self:
            return Response({"error": "Permission Denied"}, status=status.HTTP_403_FORBIDDEN)

        doctor = get_object_or_404(Doctor, pk=pk)
        serializer = DoctorSerializer(doctor, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk, *args, **kwargs):
        if request.user.role != 'admin':
            return Response({"error": "Permission Denied"}, status=status.HTTP_403_FORBIDDEN)
        doctor = get_object_or_404(Doctor, pk=pk)
        if doctor.user:
            doctor.user.delete()
        doctor.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PatientListCreateView(APIView):
    """
    GET: List patients.
    POST: Create a new patient record.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        if request.user.role == 'doctor':
            patients = Patient.objects.filter(doctor_mappings__doctor__user=request.user)
        elif request.user.role == 'admin':
            patients = Patient.objects.filter(created_by=request.user)
        else:  # patient
            patients = Patient.objects.filter(user=request.user)
        serializer = PatientSerializer(patients, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        if request.user.role not in ['admin', 'doctor']:
            return Response({"error": "Only admins and doctors can register new patients."}, status=status.HTTP_403_FORBIDDEN)
        serializer = PatientSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(created_by=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class PatientDetailView(APIView):
    """
    GET: Retrieve patient details.
    PUT: Update patient details.
    DELETE: Delete patient record.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, pk, *args, **kwargs):
        if request.user.role == 'doctor':
            patient = get_object_or_404(Patient, pk=pk, doctor_mappings__doctor__user=request.user)
        elif request.user.role == 'admin':
            patient = get_object_or_404(Patient, pk=pk, created_by=request.user)
        else:  # patient
            # Accept Patient.id or patient's CustomUser.id (pk)
            patient = Patient.objects.filter(user=request.user).first()
            if not patient:
                patient = get_object_or_404(Patient, pk=pk, user=request.user)
        serializer = PatientSerializer(patient)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk, *args, **kwargs):
        if request.user.role == 'doctor':
            patient = get_object_or_404(Patient, pk=pk, doctor_mappings__doctor__user=request.user)
        elif request.user.role == 'admin':
            patient = get_object_or_404(Patient, pk=pk, created_by=request.user)
        else:  # patient
            patient = get_object_or_404(Patient, pk=pk, user=request.user)
        serializer = PatientSerializer(patient, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk, *args, **kwargs):
        if request.user.role != 'admin':
            return Response({"error": "Only admins can delete patient profiles."}, status=status.HTTP_403_FORBIDDEN)
        patient = get_object_or_404(Patient, pk=pk, created_by=request.user)
        if patient.user:
            patient.user.delete()
        patient.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class MappingListCreateView(APIView):
    """
    GET: List doctor-patient assignments.
    POST: Assign a doctor to a patient.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        if request.user.role == 'doctor':
            mappings = PatientDoctorMapping.objects.filter(doctor__user=request.user)
        elif request.user.role == 'admin':
            mappings = PatientDoctorMapping.objects.filter(patient__created_by=request.user)
        else:  # patient
            mappings = PatientDoctorMapping.objects.filter(patient__user=request.user)
        serializer = MappingSerializer(mappings, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        if request.user.role not in ['admin', 'doctor']:
            return Response({"error": "Patients cannot create assignments."}, status=status.HTTP_403_FORBIDDEN)
        serializer = MappingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        patient = serializer.validated_data['patient_id']
        if request.user.role == 'admin' and patient.created_by != request.user:
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
        # First look up by user_id
        patient = Patient.objects.filter(user_id=patient_id).first()
        if not patient:
            # Otherwise look up by Patient.id
            patient = Patient.objects.filter(id=patient_id).first()
            
        if not patient:
            return Response({"error": "Patient not found"}, status=status.HTTP_404_NOT_FOUND)

        # Permission check
        if request.user.role == 'admin' and patient.created_by != request.user:
            return Response({"error": "Permission Denied"}, status=status.HTTP_403_FORBIDDEN)
        elif request.user.role == 'doctor':
            # check if patient assigned to doctor
            if not PatientDoctorMapping.objects.filter(patient=patient, doctor__user=request.user).exists():
                return Response({"error": "Permission Denied"}, status=status.HTTP_403_FORBIDDEN)
        elif request.user.role == 'patient' and patient.user != request.user:
            return Response({"error": "Permission Denied"}, status=status.HTTP_403_FORBIDDEN)
            
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
        if request.user.role == 'admin':
            mapping = get_object_or_404(PatientDoctorMapping, pk=pk, patient__created_by=request.user)
        elif request.user.role == 'doctor':
            mapping = get_object_or_404(PatientDoctorMapping, pk=pk, doctor__user=request.user)
        else:
            return Response({"error": "Only admins and doctors can dismiss mappings."}, status=status.HTTP_403_FORBIDDEN)
        mapping.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
