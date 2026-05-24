from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models


class CustomUserManager(BaseUserManager):
    """
    Custom manager for CustomUser model where email is the unique identifier for authentication.
    """
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        extra_fields.setdefault('is_active', True)
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    """
    Custom User Model representing the Administrator / receptionist / operator.
    Uses email as the unique identifier for logins.
    """
    ROLE_CHOICES = (
        ('admin', 'Admin/Operator'),
        ('doctor', 'Doctor'),
        ('patient', 'Patient'),
    )
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='admin')
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.email})"


class Doctor(models.Model):
    """
    Doctor Model representing doctor data entries managed by the system operators.
    Can be associated with a CustomUser for logins.
    """
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, null=True, blank=True, related_name='doctor_profile')
    name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, blank=True, default='')
    specialization = models.CharField(max_length=100)
    experience_years = models.IntegerField()
    phone = models.CharField(max_length=20)
    license_number = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Dr. {self.name} ({self.specialization})"


class Patient(models.Model):
    """
    Patient Model representing patient data entries managed by the system operators.
    Can be associated with a CustomUser for logins.
    Contains date_of_birth, blood_group, phone, address, and medical_history.
    Tracked back to the CustomUser (operator) who created it.
    """
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, null=True, blank=True, related_name='patient_profile')
    name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, blank=True, default='')
    date_of_birth = models.DateField()
    blood_group = models.CharField(max_length=10)
    phone = models.CharField(max_length=20)
    address = models.TextField()
    medical_history = models.TextField(blank=True, default='')
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='patients')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Patient {self.name} ({self.blood_group})"


class PatientDoctorMapping(models.Model):
    """
    Mapping table linking Patient and Doctor models.
    Has unique mapping constraint and custom notes.
    """
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='doctor_mappings')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='patient_mappings')
    assigned_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, default='')

    class Meta:
        unique_together = ('patient', 'doctor')
        ordering = ['-created_at']

    def __str__(self):
        return f"Mapping: {self.patient.name} -> Dr. {self.doctor.name}"
