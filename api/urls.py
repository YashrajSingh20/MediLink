from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from api.views import (
    UserRegisterView,
    LoginView,
    PatientListCreateView,
    PatientDetailView,
    DoctorListCreateView,
    DoctorDetailView,
    MappingListCreateView,
    MappingPatientDetailView,
    MappingDeleteView,
)


class MappingDetailDispatchView(APIView):
    """
    Combined router to route requests for '/api/mappings/<id>/' based on HTTP Method:
    - GET: Dispatches to MappingPatientDetailView (getting all doctors for patient_id)
    - DELETE: Dispatches to MappingDeleteView (deleting mapping by mapping id)
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, pk, *args, **kwargs):
        # We pass the URL parameter 'pk' as 'patient_id' to MappingPatientDetailView
        return MappingPatientDetailView.as_view()(request._request, patient_id=pk, *args, **kwargs)

    def delete(self, request, pk, *args, **kwargs):
        # We pass the URL parameter 'pk' as 'pk' to MappingDeleteView
        return MappingDeleteView.as_view()(request._request, pk=pk, *args, **kwargs)


urlpatterns = [
    # Auth Endpoints
    path('auth/register/', UserRegisterView.as_view(), name='register'),
    path('auth/register/doctor/', UserRegisterView.as_view(), name='register_doctor_compat'),
    path('auth/register/patient/', UserRegisterView.as_view(), name='register_patient_compat'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Patient Endpoints
    path('patients/', PatientListCreateView.as_view(), name='patient_list_create'),
    path('patients/<int:pk>/', PatientDetailView.as_view(), name='patient_detail'),

    # Doctor Endpoints
    path('doctors/', DoctorListCreateView.as_view(), name='doctor_list_create'),
    path('doctors/<int:pk>/', DoctorDetailView.as_view(), name='doctor_detail'),

    # Mapping Endpoints
    path('mappings/', MappingListCreateView.as_view(), name='mapping_list_create'),
    path('mappings/<int:pk>/', MappingDetailDispatchView.as_view(), name='mapping_detail_dispatch'),
]
