from rest_framework.permissions import BasePermission


class IsDoctor(BasePermission):
    """
    Allows access only to users with the 'doctor' role.
    """
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role == 'doctor'
        )


class IsPatient(BasePermission):
    """
    Allows access only to users with the 'patient' role.
    """
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role == 'patient'
        )


class IsAdminUser(BasePermission):
    """
    Allows access only to users with the 'admin' role.
    """
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role == 'admin'
        )


class IsDoctorOrAdmin(BasePermission):
    """
    Allows access to users with either 'doctor' or 'admin' roles.
    """
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role in ['doctor', 'admin']
        )


class IsOwnerOrAdmin(BasePermission):
    """
    Allows access to the owner of the object or an admin.
    Supports User models, Profile models, and Mapping models.
    """
    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Admins always have access
        if request.user.role == 'admin':
            return True

        # If the object itself is the user
        if obj == request.user:
            return True

        # If the object has a 'user' attribute (e.g., DoctorProfile, PatientProfile)
        if hasattr(obj, 'user') and obj.user == request.user:
            return True

        # If the object is a PatientDoctorMapping, check if the patient or doctor matches
        if hasattr(obj, 'patient') and obj.patient == request.user:
            return True
        if hasattr(obj, 'doctor') and obj.doctor == request.user:
            return True

        return False
