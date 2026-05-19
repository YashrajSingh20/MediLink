"""
This file previously contained role-based custom permission classes 
(e.g., IsDoctor, IsPatient, IsAdminUser). 

Since the database architecture has been refactored to a single-operator model,
all permission logic has been moved directly into the API views (`api/views.py`) 
using standard `IsAuthenticated` checks alongside database-level query filtering 
(e.g., `created_by=request.user`).

This file is intentionally left blank.
"""
