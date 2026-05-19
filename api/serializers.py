from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from api.models import CustomUser, Doctor, Patient, PatientDoctorMapping


class UserRegisterSerializer(serializers.ModelSerializer):
    """
    User Registration Serializer for POST /api/auth/register/.
    Validates name, email, and password.
    """
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = CustomUser
        fields = ['id', 'name', 'email', 'password', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate_email(self, value):
        if CustomUser.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            email=validated_data['email'],
            name=validated_data['name'],
            password=validated_data['password']
        )
        return user


class LoginSerializer(serializers.Serializer):
    """
    Validates email + password, authenticates credentials,
    and returns JWT tokens alongside CustomUser details.
    """
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        user = authenticate(email=email, password=password)

        if not user:
            raise serializers.ValidationError("Invalid email or password.")
        
        if not user.is_active:
            raise serializers.ValidationError("User account is deactivated.")

        # Generate tokens
        refresh = RefreshToken.for_user(user)

        return {
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user_id': user.id,
            'name': user.name,
            'email': user.email,
            'role': 'admin'  # Hardcode role to admin so frontend grants full dashboard access to operator
        }


class DoctorSerializer(serializers.ModelSerializer):
    """
    Serializer for Doctor CRUD.
    Integrates nested doctor_profile structure for 100% compatibility with frontend.
    """
    class Meta:
        model = Doctor
        fields = ['id', 'name', 'email', 'specialization', 'experience_years', 'phone', 'license_number', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate_license_number(self, value):
        # Allow updates to keep the same license number, but prevent duplicate entries
        instance = self.instance
        qs = Doctor.objects.filter(license_number__iexact=value)
        if instance:
            qs = qs.exclude(id=instance.id)
        if qs.exists():
            raise serializers.ValidationError("A doctor with this license number already exists.")
        return value

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        # Wrap profile fields under doctor_profile
        ret['doctor_profile'] = {
            'specialization': ret.pop('specialization', 'General Practice'),
            'experience_years': ret.pop('experience_years', 0),
            'phone': ret.pop('phone', ''),
            'license_number': ret.pop('license_number', ''),
        }
        return ret

    def to_internal_value(self, data):
        # Unwrap doctor_profile if present in input data
        internal_data = data.copy()
        profile_data = internal_data.pop('doctor_profile', None)
        if isinstance(profile_data, dict):
            for k, v in profile_data.items():
                internal_data[k] = v
        
        # Strip password if present since standalone doctor doesn't use it
        internal_data.pop('password', None)
        
        return super().to_internal_value(internal_data)


class PatientSerializer(serializers.ModelSerializer):
    """
    Serializer for Patient CRUD.
    Integrates nested patient_profile structure for 100% compatibility with frontend.
    """
    created_by_name = serializers.ReadOnlyField(source='created_by.name')

    class Meta:
        model = Patient
        fields = [
            'id', 'name', 'email', 'date_of_birth', 'blood_group', 'phone', 
            'address', 'medical_history', 'created_by', 'created_by_name', 'created_at'
        ]
        read_only_fields = ['id', 'created_by', 'created_by_name', 'created_at']

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        # Wrap profile fields under patient_profile
        ret['patient_profile'] = {
            'date_of_birth': ret.pop('date_of_birth', '2000-01-01'),
            'blood_group': ret.pop('blood_group', 'O+'),
            'phone': ret.pop('phone', ''),
            'address': ret.pop('address', ''),
            'medical_history': ret.pop('medical_history', ''),
        }
        return ret

    def to_internal_value(self, data):
        # Unwrap patient_profile if present in input data
        internal_data = data.copy()
        profile_data = internal_data.pop('patient_profile', None)
        if isinstance(profile_data, dict):
            for k, v in profile_data.items():
                internal_data[k] = v
                
        # Strip password if present since standalone patient doesn't use it
        internal_data.pop('password', None)
        
        return super().to_internal_value(internal_data)


class MappingSerializer(serializers.ModelSerializer):
    """
    Handles Patient-Doctor Assignments.
    - Input: Writes accept patient_id and doctor_id.
    - Output: Returns nested Patient and Doctor details.
    """
    patient_id = serializers.PrimaryKeyRelatedField(
        queryset=Patient.objects.all(),
        source='patient',
        write_only=True
    )
    doctor_id = serializers.PrimaryKeyRelatedField(
        queryset=Doctor.objects.all(),
        source='doctor',
        write_only=True
    )
    patient = PatientSerializer(read_only=True)
    doctor = DoctorSerializer(read_only=True)

    class Meta:
        model = PatientDoctorMapping
        fields = ['id', 'patient_id', 'doctor_id', 'patient', 'doctor', 'assigned_at', 'notes']
        read_only_fields = ['id', 'assigned_at']

    def validate(self, data):
        patient = data.get('patient')
        doctor = data.get('doctor')
        
        # Check if already assigned
        instance = self.instance
        qs = PatientDoctorMapping.objects.filter(patient=patient, doctor=doctor)
        if instance:
            qs = qs.exclude(id=instance.id)
        if qs.exists():
            raise serializers.ValidationError("This patient-doctor assignment already exists.")
        
        return data
