# Healthcare Backend REST API

A production-ready Django REST Framework (DRF) backend for a healthcare application. In this architecture:
- **CustomUser** represents the authenticated system operator (e.g. receptionist, staff, or admin). Users register and login via JWT tokens to manage the clinical workspace.
- **Doctor** is a standalone data table containing specialization, experience, phone, and license details.
- **Patient** is a standalone data table tracked back to the authenticated system operator (`created_by`) who added their record.
- **PatientDoctorMapping** maps assignments between Patients and Doctors.

The API features built-in serialization layers wrapping/unwrapping payloads for full compatibility with nested profiles on the premium glassmorphic SPA frontend client.

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
python manage.py makemigrations
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
| `DEBUG` | Enable/disable developer mode showing detailed debug traces. | `True` |
| `DB_NAME` | Name of the PostgreSQL database designed for this app. | `healthcare_db` |
| `DB_USER` | Username used to authenticate against the PostgreSQL server. | `postgres` |
| `DB_PASSWORD` | Password used to authenticate against the PostgreSQL server. | `yourpassword` |
| `DB_HOST` | Database server address (use `localhost` for local dev). | `localhost` |
| `DB_PORT` | Port number of your PostgreSQL server. | `5432` |
| `ALLOWED_HOSTS` | Comma-separated domains/IP addresses permitted to connect to this server. | `localhost,127.0.0.1` |

---

## 3. API Endpoints Reference & Examples

Use the following cURL examples to interact with the server. (Remember to replace `<JWT_ACCESS_TOKEN>` with your login JWT access token).

### Authentication

#### A. Register System Operator
* **Route**: `POST /api/auth/register/`
* **Access**: Public
* **cURL Request**:
```bash
curl -X POST http://127.0.0.1:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Jane Doe",
    "email": "operator@healthcare.com",
    "password": "SecurePassword123"
  }'
```

#### B. Login System Operator
* **Route**: `POST /api/auth/login/`
* **Access**: Public
* **cURL Request**:
```bash
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "operator@healthcare.com",
    "password": "SecurePassword123"
  }'
```

#### C. Refresh JWT Token
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

#### A. Create Standalone Patient
* **Route**: `POST /api/patients/`
* **Access**: Authenticated System Operator (automatically links `created_by` field)
* **cURL Request**:
```bash
curl -X POST http://127.0.0.1:8000/api/patients/ \
  -H "Authorization: Bearer <JWT_ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Peter Parker",
    "email": "spidey@dailybugle.net",
    "date_of_birth": "2001-08-10",
    "blood_group": "O-",
    "phone": "555-0909",
    "address": "Forest Hills, Queens",
    "medical_history": "Spider bite symptoms. Heightened reflexes."
  }'
```

#### B. List Patients
* **Route**: `GET /api/patients/`
* **Access**: Authenticated System Operator (returns patients created by the authenticated operator)
* **cURL Request**:
```bash
curl -X GET http://127.0.0.1:8000/api/patients/ \
  -H "Authorization: Bearer <JWT_ACCESS_TOKEN>"
```

#### C. Get Patient Details
* **Route**: `GET /api/patients/<id>/`
* **Access**: Authenticated System Operator
* **cURL Request**:
```bash
curl -X GET http://127.0.0.1:8000/api/patients/1/ \
  -H "Authorization: Bearer <JWT_ACCESS_TOKEN>"
```

#### D. Update Patient Details
* **Route**: `PUT /api/patients/<id>/`
* **Access**: Authenticated System Operator
* **cURL Request**:
```bash
curl -X PUT http://127.0.0.1:8000/api/patients/1/ \
  -H "Authorization: Bearer <JWT_ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Peter Parker Updated",
    "patient_profile": {
      "phone": "555-9999",
      "address": "New Mansion, Gotham",
      "medical_history": "Recovered from flu. Spider bite checked."
    }
  }'
```

#### E. Delete Patient
* **Route**: `DELETE /api/patients/<id>/`
* **Access**: Authenticated System Operator
* **cURL Request**:
```bash
curl -X DELETE http://127.0.0.1:8000/api/patients/1/ \
  -H "Authorization: Bearer <JWT_ACCESS_TOKEN>"
```

---

### Doctor Management

#### A. Create Standalone Doctor
* **Route**: `POST /api/doctors/`
* **Access**: Authenticated System Operator
* **cURL Request**:
```bash
curl -X POST http://127.0.0.1:8000/api/doctors/ \
  -H "Authorization: Bearer <JWT_ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Dr. Strange",
    "email": "strange@kamartaj.org",
    "specialization": "Neurosurgery",
    "experience_years": 20,
    "phone": "555-8899",
    "license_number": "LIC88888"
  }'
```

#### B. List Doctors
* **Route**: `GET /api/doctors/`
* **Access**: Authenticated System Operator
* **cURL Request**:
```bash
curl -X GET http://127.0.0.1:8000/api/doctors/ \
  -H "Authorization: Bearer <JWT_ACCESS_TOKEN>"
```

#### C. Get Doctor Details
* **Route**: `GET /api/doctors/<id>/`
* **Access**: Authenticated System Operator
* **cURL Request**:
```bash
curl -X GET http://127.0.0.1:8000/api/doctors/1/ \
  -H "Authorization: Bearer <JWT_ACCESS_TOKEN>"
```

#### D. Update Doctor Details
* **Route**: `PUT /api/doctors/<id>/`
* **Access**: Authenticated System Operator
* **cURL Request**:
```bash
curl -X PUT http://127.0.0.1:8000/api/doctors/1/ \
  -H "Authorization: Bearer <JWT_ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Dr. Strange Jr.",
    "doctor_profile": {
      "specialization": "Sorcery",
      "experience_years": 21,
      "phone": "555-1212",
      "license_number": "LIC88888"
    }
  }'
```

#### E. Delete Doctor
* **Route**: `DELETE /api/doctors/<id>/`
* **Access**: Authenticated System Operator
* **cURL Request**:
```bash
curl -X DELETE http://127.0.0.1:8000/api/doctors/1/ \
  -H "Authorization: Bearer <JWT_ACCESS_TOKEN>"
```

---

### Patient-Doctor Mappings

#### A. Assign Patient to Doctor
* **Route**: `POST /api/mappings/`
* **Access**: Authenticated System Operator
* **cURL Request**:
```bash
curl -X POST http://127.0.0.1:8000/api/mappings/ \
  -H "Authorization: Bearer <JWT_ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": 1,
    "doctor_id": 1,
    "notes": "Assigned to Neurosurgery division."
  }'
```

#### B. List Mappings
* **Route**: `GET /api/mappings/`
* **Access**: Authenticated System Operator (returns only mappings of patients created by the authenticated operator)
* **cURL Request**:
```bash
curl -X GET http://127.0.0.1:8000/api/mappings/ \
  -H "Authorization: Bearer <JWT_ACCESS_TOKEN>"
```

#### C. Get Assigned Doctors for Patient
* **Route**: `GET /api/mappings/<patient_id>/`
* **Access**: Authenticated System Operator
* **cURL Request**:
```bash
curl -X GET http://127.0.0.1:8000/api/mappings/1/ \
  -H "Authorization: Bearer <JWT_ACCESS_TOKEN>"
```

#### D. Delete Mapping
* **Route**: `DELETE /api/mappings/<id>/`
* **Access**: Authenticated System Operator
* **cURL Request**:
```bash
curl -X DELETE http://127.0.0.1:8000/api/mappings/1/ \
  -H "Authorization: Bearer <JWT_ACCESS_TOKEN>"
```

---

## 4. Error JSON Responses

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