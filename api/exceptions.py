from rest_framework.views import exception_handler
from rest_framework.exceptions import ValidationError, AuthenticationFailed, NotAuthenticated, PermissionDenied, NotFound
from rest_framework.response import Response
from rest_framework import status


def custom_exception_handler(exc, context):
    """
    Custom exception handler to return structured JSON errors as requested.
    Wraps standard DRF exceptions to follow the format:
    - 400: { "error": { "field": ["message"] } }
    - 401: { "error": "Authentication required" }
    - 403: { "error": "You do not have permission" }
    - 404: { "error": "Not found" }
    - 500: { "error": "Internal server error" }
    """
    # Call DRF's default exception handler first to get standard response
    response = exception_handler(exc, context)

    if response is not None:
        if isinstance(exc, ValidationError):
            response.data = {
                "error": response.data
            }
        elif isinstance(exc, (AuthenticationFailed, NotAuthenticated)):
            response.data = {
                "error": "Authentication required"
            }
            response.status_code = status.HTTP_401_UNAUTHORIZED
        elif isinstance(exc, PermissionDenied):
            response.data = {
                "error": "You do not have permission"
            }
            response.status_code = status.HTTP_403_FORBIDDEN
        elif isinstance(exc, NotFound):
            response.data = {
                "error": "Not found"
            }
            response.status_code = status.HTTP_404_NOT_FOUND
        else:
            # Fallback wrapper for any other DRF exceptions (e.g. MethodNotAllowed)
            detail = response.data.get('detail', str(exc))
            response.data = {
                "error": detail
            }
    else:
        # Non-DRF exception occurred (Internal Server Error)
        # We intercept it here and return custom 500 JSON response instead of default HTML
        response = Response(
            {"error": "Internal server error"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    return response
