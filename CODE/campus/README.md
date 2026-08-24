# Sol Plaatje University (SPU) Venue Management System

A robust, full-stack Venue Management System and RESTful API tailored specifically for **Sol Plaatje University (SPU)** to meet the **NADV744 Advanced Development Systems** assignment requirements.

---

## System Overview

The system allows Sol Plaatje University administrators, academic staff (Lecturers), and Student Leaders (SRC, Peer Mentors, Tutors, House Committee, etc.) to browse, book, manage, and verify availability of **62+ campus venues across 7 buildings** with automated conflict detection, strict role-based access control (RBAC), and university branding.

---

## Feature Highlights

1. **Role-Based Authentication & Permissions**
   - **Admin:** Full CRUD access to venues, buildings, user management, and booking approval/decline. Direct Django admin links removed from frontend menus for clean UX.
   - **Lecturers & Student Leaders:** Browse venues, view real-time availability, submit booking requests, cancel their own pending/approved bookings, and track status.
   - **Password Confirmation & Reset:** Mandatory password confirmation on signup, prevention of public admin registration, and forgot/reset password token workflows.

2. **Intelligent Scheduling & Conflict Prevention**
   - Operating hours enforcement (08:00 – 17:00).
   - Database-level overlap conflict detection preventing double-booking of any venue for approved slots.
   - Live availability API endpoint calculating free time slots on any chosen date.

3. **Comprehensive RESTful API**
   - Complete JSON REST API powered by Django REST Framework & SimpleJWT.
   - Standard HTTP response codes (`200 OK`, `201 Created`, `400 Bad Request`, `401 Unauthorized`, `403 Forbidden`, `404 Not Found`, `409 Conflict`, `422 Unprocessable Entity`).

---

## Quickstart & Setup Guide

### 1. Prerequisites
- Python 3.10+ (tested on Python 3.13)
- SQLite (default) or PostgreSQL

### 2. Environment Configuration
Create or inspect the `.env` file in the project root:
```env
SECRET_KEY=spu-nadv744-secure-production-secret-key-2026
DEBUG=True
ALLOWED_HOSTS=*
DB_ENGINE=sqlite
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Apply Database Migrations
```bash
python manage.py migrate
```

### 5. Seed SPU Buildings, Venues & Test Accounts
Run the automated seed command to populate the database with all 7 buildings, 62+ venues, and default accounts:
```bash
python manage.py seed_venues
```

### 6. Run the Development Server
```bash
python manage.py runserver
```
Navigate to `http://127.0.0.1:8000/` in your web browser.

---

## Default User Accounts

| Role | Email | Password | Permissions |
| :--- | :--- | :--- | :--- |
| **Administrator** | `admin@spu.ac.za` | `AdminPass123!` | Full access, venue CRUD, approval queue, user management |
| **Lecturer** | `batlang@spu.ac.za` | `batlang@spu.ac.za012` | Browse venues, request bookings, cancel own bookings |
| **Student Leader** | `walaza@spu.ac.za` | `walaza@spu.ac.za123` | Browse venues, request bookings, leadership badge |

---

## REST API Reference

### Authentication Endpoints (`/api/auth/`)

| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/auth/register` | Register Lecturer or Student Leader | No |
| `POST` | `/api/auth/login` | Obtain JWT Access & Refresh Tokens | No |
| `POST` | `/api/auth/refresh` | Refresh expired access token | No |
| `GET` | `/api/auth/me` | Retrieve authenticated user profile | Bearer Token |
| `POST` | `/api/auth/forgot-password` | Generate reset token for user email | No |
| `POST` | `/api/auth/reset-password` | Reset password using valid token | No |

#### Example: Register a User
```bash
curl -X POST http://127.0.0.1:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Dr. Jane Doe",
    "email": "jane.doe@spu.ac.za",
    "role": "lecturer",
    "password": "SecurePassword123!",
    "password_confirm": "SecurePassword123!",
    "phone_number": "+27821112233"
  }'
```

#### Example: Login & Obtain JWT
```bash
curl -X POST http://127.0.0.1:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@spu.ac.za",
    "password": "AdminPass123!"
  }'
```

---

### Venues & Buildings Endpoints (`/api/resources/`)

| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/resources/buildings` | List all 7 SPU Buildings | No |
| `GET` | `/api/resources/venues` | List & filter venues (`?building=`, `?type=`, `?search=`, `?min_capacity=`) | No |
| `POST` | `/api/resources/venues/create` | Create a new SPU venue | Admin Only |
| `GET` | `/api/resources/venues/<id>` | Venue details with building info | No |
| `PUT/PATCH` | `/api/resources/venues/<id>/update` | Update venue details | Admin Only |
| `DELETE` | `/api/resources/venues/<id>` | Delete venue | Admin Only |
| `GET` | `/api/resources/venues/<id>/availability?date=YYYY-MM-DD` | Calculate booked & free time slots | No |

#### Example: Check Real Availability
```bash
curl -X GET "http://127.0.0.1:8000/api/resources/venues/1/availability?date=2026-09-01"
```

---

### Bookings Endpoints (`/api/resources/bookings`)

| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/resources/bookings` | List user bookings (Admins see all) | Bearer Token |
| `POST` | `/api/resources/bookings` | Submit new booking request (with conflict check) | Bearer Token |
| `GET` | `/api/resources/bookings/<id>` | Retrieve booking details | Bearer Token |
| `POST` | `/api/resources/bookings/<id>/cancel` | Cancel own booking | Booker / Admin |
| `PUT/PATCH` | `/api/resources/bookings/<id>/status` | Update booking status (`approved`/`declined`) | Admin Only |

#### Example: Submit a Booking Request
```bash
curl -X POST http://127.0.0.1:8000/api/resources/bookings \
  -H "Authorization: Bearer <YOUR_ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "resource": 1,
    "booking_date": "2026-09-01",
    "start_time": "09:00:00",
    "end_time": "11:00:00",
    "purpose": "NADV744 Lab Test Session",
    "phone_number": "+27821234567"
  }'
```

---

## Automated Unit Testing

To run the automated test suite covering all authentication workflows, venue filtering, role enforcement, booking conflict prevention, and availability calculation:

```bash
python manage.py test
```

### Test Coverage Breakdown:
- `users/tests.py`:
  - `test_lecturer_registration_success`: Validates lecturer registration with password confirmation.
  - `test_student_leader_registration_success`: Validates student leader registration with leadership role tags.
  - `test_password_mismatch_fails`: Ensures mismatched passwords trigger `HTTP 422`.
  - `test_admin_registration_prevented`: Ensures public admin registration attempts are rejected.
  - `test_forgot_and_reset_password_flow`: Tests the complete token generation, password reset, and subsequent login flow.
- `resources/tests.py`:
  - `test_list_buildings_and_venues`: Validates building and venue retrieval APIs.
  - `test_venue_creation_restricted_to_admin`: Ensures non-admins receive `HTTP 403 Forbidden` on create.
  - `test_booking_creation_and_conflict_detection`: Tests booking submission, admin approval, and rejection of overlapping bookings (`HTTP 422`).
  - `test_real_availability_endpoint`: Verifies calculation of available and booked time windows.

---

## Project Architecture

```
campus/
│── manage.py
│── requirements.txt
│── README.md
│── .env
│── campus/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│── users/
│   ├── models.py          # Custom User model (roles, leadership, reset_token)
│   ├── serializers.py     # Auth & registration DRF serializers
│   ├── views.py           # Auth API views (JWT login, register, reset)
│   ├── urls.py            # /api/auth/ routes
│   ├── permissions.py     # IsAdmin, IsBooker permission classes
│   └── tests.py           # Auth unit tests
│── resources/
│   ├── models.py          # Building, Resource (Venue), Booking models + conflict detection
│   ├── serializers.py     # Venue, Building, Booking, Availability serializers
│   ├── views.py           # Resource CRUD, Booking, Availability API views
│   ├── urls.py            # /api/resources/ routes
│   └── tests.py           # Venue & Booking unit tests
│── dashboard_app/
│   ├── views.py           # Session-based UI views (Home, Venues, Bookings, Users, Auth)
│   ├── urls.py            # Web dashboard routes
│   ├── management/
│   │   └── commands/
│   │       └── seed_venues.py # SPU seed script (7 buildings, 62+ venues, test users)
│   └── templates/
│       └── dashboard/     # SPU-branded HTML templates
└── templates/
    └── base.html          # SPU Cobalt Blue & Gold base layout with responsive sidebar
```

---
*Developed for Sol Plaatje University &bull; NADV744 Advanced Development Systems*
