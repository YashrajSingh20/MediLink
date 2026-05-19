from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken

from api.models import CustomUser, DoctorProfile, PatientProfile, PatientDoctorMapping
from api.serializers import (
    DoctorRegisterSerializer,
    PatientRegisterSerializer,
    LoginSerializer,
    DoctorDetailSerializer,
    PatientDetailSerializer,
    MappingSerializer,
    UserRegisterSerializer,
)
from api.permissions import IsDoctorOrAdmin, IsAdminUser


class DoctorRegisterView(APIView):
    """
    POST only.
    Registers a new doctor user along with their doctor profile.
    Returns the created user data along with a standard JWT access token string under 'token'.
    """
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = DoctorRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Return access token on successful registration
        token = str(RefreshToken.for_user(user).access_token)
        
        return Response({
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role,
            "token": token
        }, status=status.HTTP_201_CREATED)


class PatientRegisterView(APIView):
    """
    POST only.
    Registers a new patient user along with their patient profile.
    Returns the created user data along with a standard JWT access token string under 'token'.
    """
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = PatientRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Return access token on successful registration
        token = str(RefreshToken.for_user(user).access_token)
        
        return Response({
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role,
            "token": token
        }, status=status.HTTP_201_CREATED)


class GenericRegisterView(APIView):
    """
    POST only.
    Registers a new user (patient, doctor, or admin).
    Returns the created user data along with a standard JWT access token under 'token'.
    Sets created_by parameter dynamically.
    """
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = UserRegisterSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Return access token on successful registration
        token = str(RefreshToken.for_user(user).access_token)
        
        return Response({
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role,
            "token": token
        }, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    """
    POST only.
    Authenticates email + password.
    Returns JWT access/refresh tokens alongside role, user_id, and name.
    """
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class PatientListCreateView(APIView):
    """
    GET + POST. Requires IsAuthenticated.
    - POST: Permission: IsDoctorOrAdmin. Creates patient user + profile, sets created_by, returns full patient data.
    - GET: Permission: IsAuthenticated. Retrieve all patients created by the authenticated user (or all patients if Admin).
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        if request.user.role not in ['doctor', 'admin']:
            raise PermissionDenied("You do not have permission")
            
        serializer = PatientRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Save user and explicitly set created_by to the active authenticated user
        user = serializer.save()
        user.created_by = request.user
        user.save()
        
        detail_serializer = PatientDetailSerializer(user)
        return Response(detail_serializer.data, status=status.HTTP_201_CREATED)

    def get(self, request, *args, **kwargs):
        if request.user.role == 'admin':
            patients = CustomUser.objects.filter(role='patient')
        else:
            # Strictly return all patient accounts created by this specific authenticated user
            patients = CustomUser.objects.filter(role='patient', created_by=request.user)
        
        serializer = PatientDetailSerializer(patients, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PatientDetailView(APIView):
    """
    GET + PUT + DELETE. Requires IsAuthenticated.
    - GET: Permission: IsDoctor (only if assigned) | IsAdmin | IsOwner (patient themselves).
    - PUT: Permission: IsDoctorOrAdmin. Updates patient profile, returns updated data.
    - DELETE: Permission: IsAdminUser only. Deletes user and returns 204.
    """
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        return get_object_or_404(CustomUser, id=pk, role='patient')

    def get(self, request, pk, *args, **kwargs):
        patient = self.get_object(pk)
        
        # Check specific permission: Admin, Assigned Doctor, or Patient themselves
        if request.user.role == 'admin':
            pass
        elif request.user.role == 'patient' and request.user.id == patient.id:
            pass
        elif request.user.role == 'doctor':
            if not PatientDoctorMapping.objects.filter(doctor=request.user, patient=patient).exists():
                raise PermissionDenied("You do not have permission")
        else:
            raise PermissionDenied("You do not have permission")

        serializer = PatientDetailSerializer(patient)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk, *args, **kwargs):
        if request.user.role not in ['doctor', 'admin']:
            raise PermissionDenied("You do not have permission")

        patient = self.get_object(pk)
        serializer = PatientDetailSerializer(patient, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk, *args, **kwargs):
        if request.user.role != 'admin':
            raise PermissionDenied("You do not have permission")

        patient = self.get_object(pk)
        patient.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class DoctorListCreateView(APIView):
    """
    GET + POST. Requires IsAuthenticated.
    - POST: Permission: IsAdminUser. Creates doctor user + profile.
    - GET: Permission: IsAuthenticated (all roles can view doctor list).
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        if request.user.role != 'admin':
            raise PermissionDenied("You do not have permission")
        
        serializer = DoctorRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        detail_serializer = DoctorDetailSerializer(user)
        return Response(detail_serializer.data, status=status.HTTP_201_CREATED)

    def get(self, request, *args, **kwargs):
        doctors = CustomUser.objects.filter(role='doctor')
        serializer = DoctorDetailSerializer(doctors, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class DoctorDetailView(APIView):
    """
    GET + PUT + DELETE. Requires IsAuthenticated.
    - GET: Permission: IsAuthenticated (all roles can view doctor details).
    - PUT: Permission: IsAdminUser | IsOwner (doctor themselves).
    - DELETE: Permission: IsAdminUser only. Deletes user and returns 204.
    """
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        return get_object_or_404(CustomUser, id=pk, role='doctor')

    def get(self, request, pk, *args, **kwargs):
        doctor = self.get_object(pk)
        serializer = DoctorDetailSerializer(doctor)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk, *args, **kwargs):
        doctor = self.get_object(pk)
        
        # Check permissions: Admin or Owner (doctor themselves)
        if request.user.role == 'admin':
            pass
        elif request.user.role == 'doctor' and request.user.id == doctor.id:
            pass
        else:
            raise PermissionDenied("You do not have permission")

        serializer = DoctorDetailSerializer(doctor, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk, *args, **kwargs):
        if request.user.role != 'admin':
            raise PermissionDenied("You do not have permission")

        doctor = self.get_object(pk)
        doctor.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class MappingListCreateView(APIView):
    """
    GET + POST. Requires IsAuthenticated.
    - POST: Permission: IsDoctorOrAdmin. Assigns doctor to patient.
    - GET: Permission: IsDoctor (returns only their own mappings) or IsAdmin (returns all mappings).
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        if request.user.role not in ['doctor', 'admin']:
            raise PermissionDenied("You do not have permission")
        
        serializer = MappingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get(self, request, *args, **kwargs):
        if request.user.role == 'admin':
            mappings = PatientDoctorMapping.objects.all()
        elif request.user.role == 'doctor':
            mappings = PatientDoctorMapping.objects.filter(doctor=request.user)
        else:
            raise PermissionDenied("You do not have permission")

        serializer = MappingSerializer(mappings, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class MappingPatientDetailView(APIView):
    """
    GET by patient_id. Requires IsAuthenticated.
    - GET: Permission: IsDoctor (if assigned to that patient) | IsAdmin | IsOwner (patient themselves).
    Returns all doctors assigned to that specific patient as a list of Doctor objects.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, patient_id, *args, **kwargs):
        patient_user = get_object_or_404(CustomUser, id=patient_id, role='patient')
        
        # Check permissions: Admin, Patient themselves, or Assigned Doctor
        if request.user.role == 'admin':
            pass
        elif request.user.role == 'patient' and request.user.id == patient_user.id:
            pass
        elif request.user.role == 'doctor':
            if not PatientDoctorMapping.objects.filter(doctor=request.user, patient=patient_user).exists():
                raise PermissionDenied("You do not have permission")
        else:
            raise PermissionDenied("You do not have permission")

        # Get all doctor user records assigned to this patient
        mappings = PatientDoctorMapping.objects.filter(patient=patient_user)
        doctors = [m.doctor for m in mappings]
        
        serializer = DoctorDetailSerializer(doctors, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class MappingDeleteView(APIView):
    """
    DELETE by mapping id. Requires IsAuthenticated.
    - DELETE: Permission: IsDoctorOrAdmin. Deletes the specific patient-doctor mapping.
    """
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk, *args, **kwargs):
        mapping = get_object_or_404(PatientDoctorMapping, id=pk)
        
        # Check permissions: Admin, or the Doctor associated with this mapping
        if request.user.role == 'admin':
            pass
        elif request.user.role == 'doctor' and mapping.doctor.id == request.user.id:
            pass
        else:
            raise PermissionDenied("You do not have permission")

        mapping.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
