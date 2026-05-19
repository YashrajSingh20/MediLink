from django.core.management.base import BaseCommand
from django.db import transaction
from api.models import CustomUser, DoctorProfile, PatientProfile, PatientDoctorMapping


class Command(BaseCommand):
    """
    Management command to seed the database with mock healthcare data:
    - 1 Admin
    - 2 Doctors (with DoctorProfiles)
    - 3 Patients (with PatientProfiles)
    - 3 Patient-Doctor Mappings (assigning each patient to one doctor)
    Wraps entire operation inside transaction.atomic() to ensure clean states.
    Can be run multiple times safely.
    """
    help = 'Seeds the database with 1 admin, 2 doctors, 3 patients, and assigns each patient to 1 doctor.'

    def handle(self, *args, **options):
        self.stdout.write('Seeding mock healthcare database...')

        # List of emails to clean up for an idempotent seeding run
        emails_to_clean = [
            'admin@healthcare.com',
            'doctor1@healthcare.com',
            'doctor2@healthcare.com',
            'patient1@healthcare.com',
            'patient2@healthcare.com',
            'patient3@healthcare.com',
        ]

        try:
            with transaction.atomic():
                # Clean up existing seed data
                deleted_count, _ = CustomUser.objects.filter(email__in=emails_to_clean).delete()
                if deleted_count > 0:
                    self.stdout.write(self.style.WARNING(f'Cleared {deleted_count} old seed records for clean slate.'))

                # 1. Create Admin
                admin_user = CustomUser.objects.create_superuser(
                    email='admin@healthcare.com',
                    password='AdminPassword123',
                    name='Admin User'
                )
                self.stdout.write(self.style.SUCCESS(f'Created Admin: {admin_user.name} ({admin_user.email})'))

                # 2. Create Doctors
                d1 = CustomUser.objects.create_user(
                    email='doctor1@healthcare.com',
                    password='DoctorPassword123',
                    name='Dr. Alice Smith',
                    role='doctor'
                )
                DoctorProfile.objects.create(
                    user=d1,
                    specialization='Cardiology',
                    experience_years=12,
                    phone='555-0101',
                    license_number='LIC12345'
                )
                self.stdout.write(self.style.SUCCESS(f'Created Doctor: {d1.name} ({d1.email})'))

                d2 = CustomUser.objects.create_user(
                    email='doctor2@healthcare.com',
                    password='DoctorPassword123',
                    name='Dr. Bob Jones',
                    role='doctor'
                )
                DoctorProfile.objects.create(
                    user=d2,
                    specialization='Pediatrics',
                    experience_years=8,
                    phone='555-0102',
                    license_number='LIC67890'
                )
                self.stdout.write(self.style.SUCCESS(f'Created Doctor: {d2.name} ({d2.email})'))

                # 3. Create Patients
                p1 = CustomUser.objects.create_user(
                    email='patient1@healthcare.com',
                    password='PatientPassword123',
                    name='John Doe',
                    role='patient'
                )
                PatientProfile.objects.create(
                    user=p1,
                    date_of_birth='1990-05-15',
                    blood_group='O+',
                    phone='555-0201',
                    address='123 Main St, New York',
                    medical_history='No major chronic medical conditions. Minor flu in Jan 2026.'
                )
                self.stdout.write(self.style.SUCCESS(f'Created Patient: {p1.name} ({p1.email})'))

                p2 = CustomUser.objects.create_user(
                    email='patient2@healthcare.com',
                    password='PatientPassword123',
                    name='Jane Miller',
                    role='patient'
                )
                PatientProfile.objects.create(
                    user=p2,
                    date_of_birth='1985-11-20',
                    blood_group='A-',
                    phone='555-0202',
                    address='456 Elm St, Los Angeles',
                    medical_history='Asthma patient since childhood. Takes inhaler daily.'
                )
                self.stdout.write(self.style.SUCCESS(f'Created Patient: {p2.name} ({p2.email})'))

                p3 = CustomUser.objects.create_user(
                    email='patient3@healthcare.com',
                    password='PatientPassword123',
                    name='Charlie Brown',
                    role='patient'
                )
                PatientProfile.objects.create(
                    user=p3,
                    date_of_birth='1995-02-10',
                    blood_group='B+',
                    phone='555-0203',
                    address='789 Oak St, Chicago',
                    medical_history='Mild Hypertension. Advised low sodium diet.'
                )
                self.stdout.write(self.style.SUCCESS(f'Created Patient: {p3.name} ({p3.email})'))

                # 4. Create Mappings
                m1 = PatientDoctorMapping.objects.create(
                    patient=p1,
                    doctor=d1,
                    notes='Patient scheduled for monthly cardiac assessment.'
                )
                self.stdout.write(self.style.SUCCESS(f'Assigned Patient {p1.name} -> Doctor {d1.name}'))

                m2 = PatientDoctorMapping.objects.create(
                    patient=p2,
                    doctor=d2,
                    notes='Consultation for seasonal asthma flareups.'
                )
                self.stdout.write(self.style.SUCCESS(f'Assigned Patient {p2.name} -> Doctor {d2.name}'))

                m3 = PatientDoctorMapping.objects.create(
                    patient=p3,
                    doctor=d1,
                    notes='Hypertension consultation. Checking blood pressure daily.'
                )
                self.stdout.write(self.style.SUCCESS(f'Assigned Patient {p3.name} -> Doctor {d1.name}'))

            self.stdout.write(self.style.SUCCESS('Seeding operations completed successfully!'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Seeding failed: {str(e)}'))
