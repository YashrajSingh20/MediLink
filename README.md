# Healthcare Backend REST API

A production-ready Django REST Framework (DRF) backend for a healthcare application. It includes user registration and profile management for Doctors and Patients, secure token-based JWT authentication, custom roles ('doctor', 'patient', 'admin'), a flexible Patient-Doctor assignment model, and customized exception handlers mapping every single response to robust, structured JSON.

---

## Technical Stack
- **Python**: 3.11+
- **Django**: 4.2+
- **Django REST Framework**: 3.14+
- **djangorestframework-simplejwt**: 5.3+
- **PostgreSQL**: configured via `.env` (using `psycopg2-binary`)
- **python-decouple**: secure settings decoupling

---

## 1. Setup Instructions

Follow these steps to run the application locally:

### Step 1: Clone or Navigate to the Directory
Ensure you are in the project folder:
```bash
cd healthcare_backend
```

### Step 2: Set Up Virtual Environment
Create and activate a Python virtual environment:
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
Install all required Python packages listed in `requirements.txt`:
```bash
pip install -r requirements.txt
```

### Step 4: Configure PostgreSQL Database & environment variables
Create a `.env` file in the root `healthcare_backend/` folder (or edit the created one). Make sure you have a running PostgreSQL instance with a database matching the details in your `.env`:
```ini
SECRET_KEY=your-secret-key-here
DEBUG=True
DB_NAME=healthcare_db
DB_USER=postgres
DB_PASSWORD=yourpassword
DB_HOST=localhost
DB_PORT=5432
ALLOWED_HOSTS=localhost,127.0.0.1
```

### Step 5: Run Database Migrations
Generate and run migrations to create the database schemas:
```bash
python manage.py makemigrations api
python manage.py migrate
```

### Step 6: Start Server
Run the local development server:
```bash
python manage.py runserver
```
The server will start running at `http://127.0.0.1:8000/`.

---

## 2. Environment Variables (`.env`)

| Variable | Description | Default / Example |
| :--- | :--- | :--- |
| `SECRET_KEY` | Unique Django secret key used for signing cryptographic tokens and JWT signatures. | `your-secret-key` |
| `DEBUG` | Enable/disable developer mode showing detailed debug traces. Set to `False` in prod. | `True` |
| `DB_NAME` | Name of the PostgreSQL database designed for this app. | `healthcare_db` |
| `DB_USER` | Username used to authenticate against the PostgreSQL server. | `postgres` |
| `DB_PASSWORD` | Password used to authenticate against the PostgreSQL server. | `yourpassword` |
| `DB_HOST` | Database server address (use `localhost` for local dev). | `localhost` |
| `DB_PORT` | Port number of your PostgreSQL server. | `5432` |
| `ALLOWED_HOSTS` | Comma-separated domains/IP addresses permitted to connect to this server. | `localhost,127.0.0.1` |

---

## 3. Database Seeding (`seed_data`)

We have written an idempotent seeding command to let you populate the database with a standard set of users and assignments.
To run the seed script:
```bash
python manage.py seed_data
```

This script will automatically clear any conflicting mock records and create:
1. **1 Admin User**: `admin@healthcare.com` (password: `AdminPassword123`)
2. **2 Doctors**:
   - `doctor1@healthcare.com` (password: `DoctorPassword123`, Spec: Cardiology)
   - `doctor2@healthcare.com` (password: `DoctorPassword123`, Spec: Pediatrics)
3. **3 Patients**:
   - `patient1@healthcare.com` (password: `PatientPassword123`)
   - `patient2@healthcare.com` (password: `PatientPassword123`)
   - `patient3@healthcare.com` (password: `PatientPassword123`)
4. **3 Assignments**:
   - Assigned `John Doe` -> `Dr. Alice Smith`
   - Assigned `Jane Miller` -> `Dr. Bob Jones`
   - Assigned `Charlie Brown` -> `Dr. Alice Smith`

---

## 4. API Endpoints Reference & Examples

Use the following cURL examples to interact with the server. (Remember to replace `<JWT_ACCESS_TOKEN>` with your login JWT access token).

### Authentication

#### A. Register Doctor
* **Route**: `POST /api/auth/register/doctor/`
* **Access**: Public
* **cURL Request**:
```bash
curl -X POST http://127.0.0.1:8000/api/auth/register/doctor/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Dr. Sarah Connor",
    "email": "sarah.connor@healthcare.com",
    "password": "SecurePassword123",
    "specialization": "Neurology",
    "experience_years": 15,
    "phone": "555-9090",
    "license_number": "LIC90909"
  }'
```

#### B. Register Patient
* **Route**: `POST /api/auth/register/patient/`
* **Access**: Public
* **cURL Request**:
```bash
curl -X POST http://127.0.0.1:8000/api/auth/register/patient/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Bruce Wayne",
    "email": "bruce.wayne@waynecorp.com",
    "password": "BatmanPassword123",
    "date_of_birth": "1980-04-17",
    "blood_group": "AB+",
    "phone": "555-8888",
    "address": "Wayne Manor, Gotham City"
  }'
```

#### C. Login User
* **Route**: `POST /api/auth/login/`
* **Access**: Public
* **cURL Request**:
```bash
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "doctor1@healthcare.com",
    "password": "DoctorPassword123"
  }'
```

#### D. Refresh JWT Token
* **Route**: `POST /api/auth/token/refresh/`
* **Access**: Public
* **cURL Request**:
```bash
curl -X POST http://127.0.0.1:8000/api/auth/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "<JWT_REFRESH_TOKEN>"
  }'
```

---

### Patient Management

#### A. Create Patient Profile
* **Route**: `POST /api/patients/`
* **Access**: Authenticated Doctors or Admins
* **cURL Request**:
```bash
curl -X POST http://127.0.0.1:8000/api/patients/ \
  -H "Authorization: Bearer <JWT_ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Peter Parker",
    "email": "spidey@dailybugle.net",
    "password": "SpideyPassword123",
    "date_of_birth": "2001-08-10",
    "blood_group": "O-",
    "phone": "555-0909",
    "address": "Forest Hills, Queens",
    "medical_history": "Spider bite symptoms. Heightened reflexes."
  }'
```

#### B. List Patients
* **Route**: `GET /api/patients/`
* **Access**: Authenticated Doctors (returns only assigned patients) or Admins (returns all patients)
* **cURL Request**:
```bash
curl -X GET http://127.0.0.1:8000/api/patients/ \
  -H "Authorization: Bearer <JWT_ACCESS_TOKEN>"
```

#### C. Get Patient Details
* **Route**: `GET /api/patients/<id>/`
* **Access**: Admin | Assigned Doctor | The Patient themselves
* **cURL Request**:
```bash
curl -X GET http://127.0.0.1:8000/api/patients/4/ \
  -H "Authorization: Bearer <JWT_ACCESS_TOKEN>"
```

#### D. Update Patient Profile
* **Route**: `PUT /api/patients/<id>/`
* **Access**: Doctor or Admin
* **cURL Request**:
```bash
curl -X PUT http://127.0.0.1:8000/api/patients/4/ \
  -H "Authorization: Bearer <JWT_ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Peter Parker Updated",
    "patient_profile": {
      "phone": "555-9999",
      "medical_history": "Recovered from flu. Spider bite checked."
    }
  }'
```

#### E. Delete Patient
* **Route**: `DELETE /api/patients/<id>/`
* **Access**: Admins Only
* **cURL Request**:
```bash
curl -X DELETE http://127.0.0.1:8000/api/patients/4/ \
  -H "Authorization: Bearer <JWT_ACCESS_TOKEN>"
```

---

### Doctor Management

#### A. Create Doctor Profile
* **Route**: `POST /api/doctors/`
* **Access**: Admins Only
* **cURL Request**:
```bash
curl -X POST http://127.0.0.1:8000/api/doctors/ \
  -H "Authorization: Bearer <JWT_ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Dr. Strange",
    "email": "strange@kamartaj.org",
    "password": "PortalPassword123",
    "specialization": "Neurosurgery",
    "experience_years": 20,
    "phone": "555-8899",
    "license_number": "LIC88888"
  }'
```

#### B. List Doctors
* **Route**: `GET /api/doctors/`
* **Access**: Authenticated (All Roles)
* **cURL Request**:
```bash
curl -X GET http://127.0.0.1:8000/api/doctors/ \
  -H "Authorization: Bearer <JWT_ACCESS_TOKEN>"
```

#### C. Get Doctor Details
* **Route**: `GET /api/doctors/<id>/`
* **Access**: Authenticated (All Roles)
* **cURL Request**:
```bash
curl -X GET http://127.0.0.1:8000/api/doctors/2/ \
  -H "Authorization: Bearer <JWT_ACCESS_TOKEN>"
```

#### D. Update Doctor Profile
* **Route**: `PUT /api/doctors/<id>/`
* **Access**: Admin | The Doctor themselves
* **cURL Request**:
```bash
curl -X PUT http://127.0.0.1:8000/api/doctors/2/ \
  -H "Authorization: Bearer <JWT_ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Dr. Alice Smith Jr.",
    "doctor_profile": {
      "experience_years": 13,
      "phone": "555-1212"
    }
  }'
```

#### E. Delete Doctor
* **Route**: `DELETE /api/doctors/<id>/`
* **Access**: Admins Only
* **cURL Request**:
```bash
curl -X DELETE http://127.0.0.1:8000/api/doctors/2/ \
  -H "Authorization: Bearer <JWT_ACCESS_TOKEN>"
```

---

### Patient-Doctor Mappings

#### A. Assign Patient to Doctor
* **Route**: `POST /api/mappings/`
* **Access**: Doctors or Admins
* **cURL Request**:
```bash
curl -X POST http://127.0.0.1:8000/api/mappings/ \
  -H "Authorization: Bearer <JWT_ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": 4,
    "doctor_id": 2,
    "notes": "Assigned to Pediatrics division."
  }'
```

#### B. List Mappings
* **Route**: `GET /api/mappings/`
* **Access**: Doctor (returns only their own mappings) | Admin (returns all mappings)
* **cURL Request**:
```bash
curl -X GET http://127.0.0.1:8000/api/mappings/ \
  -H "Authorization: Bearer <JWT_ACCESS_TOKEN>"
```

#### C. Get Assigned Doctors for Patient
* **Route**: `GET /api/mappings/<patient_id>/`
* **Access**: Admin | Assigned Doctor | The Patient themselves
* **cURL Request**:
```bash
curl -X GET http://127.0.0.1:8000/api/mappings/4/ \
  -H "Authorization: Bearer <JWT_ACCESS_TOKEN>"
```

#### D. Delete Mapping
* **Route**: `DELETE /api/mappings/<id>/`
* **Access**: Doctor (must be involved in the mapping) | Admin
* **cURL Request**:
```bash
curl -X DELETE http://127.0.0.1:8000/api/mappings/1/ \
  -H "Authorization: Bearer <JWT_ACCESS_TOKEN>"
```

---

## 5. Error JSON Responses

The backend formats all API errors into structured, predictable JSON schemas:

* **400 Validation Error**:
```json
{
  "error": {
    "email": ["A user with this email already exists."],
    "license_number": ["This field must be unique."]
  }
}
```

* **401 Unauthenticated**:
```json
{
  "error": "Authentication required"
}
```

* **403 Wrong Role / Access Blocked**:
```json
{
  "error": "You do not have permission"
}
```

* **404 Not Found**:
```json
{
  "error": "Not found"
}
```

* **500 Server Error**:
```json
{
  "error": "Internal server error"
}
```
#   M e d i L i n k  
 #   M e d i L i n k  
 