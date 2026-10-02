# EduSub — Web-based Application

> Substitute Teacher Coordination Platform  
> FHNW — Web-based Applications (HS26) | Dr. Devid Montecchiari  
> **Milestone 1 — Design**

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Team](#2-team)
3. [Tech Stack](#3-tech-stack)
4. [User Roles](#4-user-roles)
5. [User Stories](#5-user-stories)
6. [Workflow Table](#6-workflow-table)
7. [API Design (Sample JSON)](#7-api-design-sample-json)
8. [Wireframes](#8-wireframes)
9. [Data Models](#9-data-models)
10. [Project Structure (planned)](#10-project-structure-planned)

---

## 1. Project Overview

**EduSub** is a browser-based substitute teacher coordination platform built for a single primary school covering Kindergarten (KG1, KG2) and Primary grades (1a–6b).

The platform digitises the process of finding and assigning substitute teachers when a class cannot be covered by its regular teacher. It provides two role-specific portals — Admin and Teacher — each with dedicated functionality.

### Problem

Schools currently coordinate substitute assignments via phone calls, WhatsApp groups, and Excel sheets. This creates gaps, missed assignments, and no audit trail.

### Solution

EduSub provides:
- A structured **substitute request** flow (date, grade, subject, time slot, notes)
- A **teacher application** system (teachers self-assign to open requests with expiry countdowns)
- An **admin approval** layer (admins confirm assignments, manage users, close requests)
- A **teacher onboarding** flow including document upload and account approval
- A **teacher profile** system (profile picture, bio, subjects, personal staff number)

This module rebuilds EduSub from a NiceGUI monolith (Advanced Programming, SS26) into a proper **FastAPI REST backend** and **React (Vite) frontend** with JWT-based authentication and a clean API/UI separation.

**GitHub Repository:** https://github.com/uAhmet1907/Web-based

---

## 2. Team

| Member | Responsibilities |
|--------|-----------------|
| Member A | Authentication endpoints, user model, database setup, JWT integration |
| Member B | Admin dashboard, RequestService, ApplicationService, backend tests |
| Member C | Teacher dashboard, profile pages, frontend components, documentation |

---

## 3. Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Python 3.12+, FastAPI, SQLModel, SQLite |
| Authentication | JWT (python-jose), bcrypt (passlib) |
| Frontend | React 18, Vite, Tailwind CSS |
| API Communication | REST / JSON |
| Testing | pytest, pytest-asyncio, httpx (TestClient) |
| Dev Tools | Uvicorn, ESLint, Prettier |

---

## 4. User Roles

| Role | Description |
|------|-------------|
| **Admin** | School administrator. Creates substitute requests, reviews teacher applications, approves/rejects teacher accounts, manages users, closes requests. |
| **Teacher** | Registered substitute teacher. Browses open requests, submits and withdraws applications, tracks application status, manages their profile. |

> All routes require a valid JWT token. Teachers additionally require `is_approved = true` before they can log in.

---

## 5. User Stories

### Admin

| ID | As an admin, I want to… | So that… |
|----|-------------------------|----------|
| A-01 | Log in with email and password | I can access the admin dashboard securely |
| A-02 | Create a substitute request with date, grade, subject, time slot and notes | Teachers know exactly what coverage is needed |
| A-03 | View all substitute requests in a table with status | I have a full overview of all coverage gaps |
| A-04 | See the details of a request (grade, subject, date, notes, expiry) | I can review what was created |
| A-05 | See which teachers have applied for a request | I can pick the most suitable substitute |
| A-06 | Approve or reject a teacher's application | The assignment is confirmed and the request is marked filled |
| A-07 | Close a substitute request manually | Outdated or filled requests are archived |
| A-08 | View all registered teachers and their approval status | I have an overview of who is on the platform |
| A-09 | View a teacher's full profile including documents and subjects | I can verify their qualifications |
| A-10 | Approve or reject a newly registered teacher account | Only verified teachers can access the platform |
| A-11 | View aggregated dashboard stats (open requests, pending applications, pending teachers) | I get an instant overview without navigating multiple pages |
| A-12 | Log out | My session is ended securely |

### Teacher

| ID | As a teacher, I want to… | So that… |
|----|--------------------------|----------|
| T-01 | Register with my name, email, phone, password and subjects | I can request access to the platform |
| T-02 | Upload my CV and teaching certificates during registration | The admin can verify my qualifications |
| T-03 | Log in with email and password after my account is approved | I can access the teacher dashboard |
| T-04 | Browse all open substitute requests | I can find available assignments |
| T-05 | Filter requests by educational level (KG / Primary) | I only see relevant assignments for my qualifications |
| T-06 | See the time remaining before a request expires | I know how urgently I need to apply |
| T-07 | Apply for an open substitute request | I can express interest in a specific coverage slot |
| T-08 | See if I have already applied for a request | I avoid applying twice |
| T-09 | View all my applications with their current status (pending / approved / rejected) | I can track where each application stands |
| T-10 | Withdraw a pending application | I can back out if my availability changes |
| T-11 | View my confirmed assignments | I know exactly when and where I am teaching |
| T-12 | Edit my profile (name, phone, bio, subjects, profile picture) | My information stays accurate |
| T-13 | Change my password | I can keep my account secure |
| T-14 | Log out | My session is ended securely |

---

## 6. Workflow Table

| # | Workflow | Actor(s) | Steps | Outcome |
|---|----------|----------|-------|---------|
| W-01 | Teacher Registration & Approval | Teacher → Admin | 1. Teacher fills registration form (name, email, phone, password, subjects). 2. Teacher uploads documents (PDF/JPG/PNG). 3. Account created with `is_approved = false`. 4. Admin reviews profile and documents. 5. Admin approves or rejects. | Teacher can log in (approved) or account is deleted (rejected). |
| W-02 | Create Substitute Request | Admin | 1. Admin opens "New Request" form. 2. Enters date, grade, subject (dynamically filtered by grade), time slot, notes. 3. Submits. 4. System creates request with status `open` and calculates `expires_at` (12h before assignment start). | Request is visible to all approved teachers. |
| W-03 | Teacher Applies for Request | Teacher | 1. Teacher browses open, non-expired requests. 2. Filters by level (KG / Primary) if needed. 3. Clicks "Apply". 4. System creates application with status `pending`. | Admin sees new application; teacher sees "Applied" badge on the request. |
| W-04 | Admin Approves Application | Admin → Teacher | 1. Admin views pending applications. 2. Opens teacher profile to verify qualifications. 3. Approves one application → status becomes `approved`. 4. Request status automatically changes to `filled`. | Teacher sees confirmed assignment; request is no longer open. |
| W-05 | Teacher Withdraws Application | Teacher | 1. Teacher views "My Applications" list. 2. Clicks "Withdraw" on a pending application. 3. System deletes the application. | Teacher is removed from the applicant list; request returns to open if no other approved application exists. |
| W-06 | Admin Closes Request | Admin | 1. Admin opens the requests table. 2. Clicks "Close" on a filled or outdated request. 3. System sets status to `closed`. | Request is archived; no new applications accepted. |
| W-07 | Request Expires Automatically | System | 1. System checks `expires_at` on all open requests. 2. Requests past expiry are automatically deleted. | Platform stays clean; teachers only see actionable requests. |
| W-08 | Teacher Updates Profile | Teacher | 1. Teacher opens profile page. 2. Edits name, phone, bio, subjects or uploads new profile picture. 3. Saves. | Teacher's profile is updated in the database. |
| W-09 | Teacher Changes Password | Teacher | 1. Teacher submits current password + new password. 2. Backend verifies current password, hashes and saves the new one. | Password is updated; existing JWT remains valid until expiry. |
| W-10 | Login (any role) | Admin / Teacher | 1. User enters email and password. 2. Backend verifies credentials; checks `is_approved` for teachers. 3. Issues JWT access token. | User is redirected to their role-specific dashboard. |
| W-11 | Logout | Admin / Teacher | 1. User clicks "Logout". 2. Frontend deletes the JWT from storage. 3. User is redirected to the login page. | Session is terminated client-side. |

---

## 7. API Design (Sample JSON)

All endpoints are prefixed with `/api/v1`. Authentication is via `Authorization: Bearer <token>` header.

---

### 7.1 Auth

#### `POST /api/v1/auth/login`

**Request**
```json
{
  "email": "admin@edusub.ch",
  "password": "admin123"
}
```

**Response `200 OK`**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "role": "admin"
}
```

#### `POST /api/v1/auth/register`

**Request**
```json
{
  "full_name": "Anna Müller",
  "email": "anna.mueller@edusub.ch",
  "phone": "0791234567",
  "password": "securepass",
  "subjects": [1, 3, 7]
}
```

**Response `201 Created`**
```json
{
  "id": 5,
  "email": "anna.mueller@edusub.ch",
  "is_approved": false,
  "message": "Registration successful. Waiting for admin approval."
}
```

#### `POST /api/v1/auth/change-password`

**Request**
```json
{
  "current_password": "securepass",
  "new_password": "newsecurepass"
}
```

**Response `200 OK`**
```json
{
  "message": "Password updated successfully."
}
```

---

### 7.2 Substitute Requests

#### `GET /api/v1/requests`

**Response `200 OK`**
```json
[
  {
    "id": 12,
    "date": "2026-10-15",
    "grade": "3a",
    "subject": { "id": 3, "name": "Mathematics" },
    "time_slot": "08:00-12:00",
    "note": "Please bring exercise sheets.",
    "reason": "Illness",
    "status": "open",
    "expires_at": "2026-10-14T20:00:00Z",
    "created_at": "2026-10-02T09:00:00Z",
    "created_by": { "id": 1, "name": "Admin Schulhaus" }
  }
]
```

#### `POST /api/v1/requests` *(Admin only)*

**Request**
```json
{
  "date": "2026-10-15",
  "grade": "3a",
  "subject_id": 3,
  "time_slot": "08:00-12:00",
  "note": "Please bring exercise sheets."
}
```

**Response `201 Created`**
```json
{
  "id": 13,
  "date": "2026-10-15",
  "grade": "3a",
  "subject_id": 3,
  "time_slot": "08:00-12:00",
  "status": "open",
  "expires_at": "2026-10-14T20:00:00Z"
}
```

#### `GET /api/v1/requests/{id}/applications` *(Admin only)*

**Response `200 OK`**
```json
[
  {
    "id": 8,
    "teacher": { "id": 5, "full_name": "Anna Müller", "personal_number": "T-0042" },
    "status": "pending",
    "applied_at": "2026-10-03T11:30:00Z"
  }
]
```

#### `PATCH /api/v1/requests/{id}/close` *(Admin only)*

**Response `200 OK`**
```json
{
  "id": 12,
  "status": "closed"
}
```

---

### 7.3 Applications

#### `POST /api/v1/requests/{request_id}/applications` *(Teacher only)*

**Response `201 Created`**
```json
{
  "id": 8,
  "request_id": 12,
  "teacher_id": 5,
  "status": "pending",
  "applied_at": "2026-10-03T11:30:00Z"
}
```

#### `GET /api/v1/applications/my` *(Teacher only)*

**Response `200 OK`**
```json
[
  {
    "id": 8,
    "request": {
      "id": 12,
      "date": "2026-10-15",
      "grade": "3a",
      "subject": { "id": 3, "name": "Mathematics" },
      "time_slot": "08:00-12:00"
    },
    "status": "pending",
    "applied_at": "2026-10-03T11:30:00Z"
  }
]
```

#### `PATCH /api/v1/applications/{id}/approve` *(Admin only)*

**Response `200 OK`**
```json
{
  "id": 8,
  "status": "approved",
  "request": { "id": 12, "status": "filled" }
}
```

#### `DELETE /api/v1/applications/{id}` *(Teacher — own pending application only)*

**Response `204 No Content`**

---

### 7.4 Subjects

#### `GET /api/v1/subjects`

**Response `200 OK`**
```json
[
  { "id": 1, "name": "German",      "level": "primary", "grades": "1-6" },
  { "id": 2, "name": "Mathematics", "level": "primary", "grades": "1-6" },
  { "id": 3, "name": "French",      "level": "primary", "grades": "3-6" },
  { "id": 4, "name": "English",     "level": "primary", "grades": "5-6" },
  { "id": 5, "name": "Free Play",   "level": "kg",      "grades": "KG"  }
]
```

---

### 7.5 Teachers (Admin view)

#### `GET /api/v1/teachers` *(Admin only)*

**Response `200 OK`**
```json
[
  {
    "id": 5,
    "full_name": "Anna Müller",
    "personal_number": "T-0042",
    "email": "anna.mueller@edusub.ch",
    "phone": "0791234567",
    "is_approved": false,
    "subjects": [{ "id": 3, "name": "Mathematics" }]
  }
]
```

#### `GET /api/v1/teachers/{id}` *(Admin only)*

**Response `200 OK`**
```json
{
  "id": 5,
  "full_name": "Anna Müller",
  "personal_number": "T-0042",
  "email": "anna.mueller@edusub.ch",
  "phone": "0791234567",
  "bio": "Experienced primary school teacher with 5 years in Basel.",
  "profile_picture": "/uploads/profile_pictures/user_5.jpg",
  "documents": ["cv_anna.pdf", "certificate_math.pdf"],
  "is_approved": false,
  "subjects": [
    { "id": 3, "name": "Mathematics" },
    { "id": 7, "name": "English" }
  ]
}
```

#### `PATCH /api/v1/teachers/{id}/approve` *(Admin only)*

**Request**
```json
{ "approved": true }
```

**Response `200 OK`**
```json
{
  "id": 5,
  "is_approved": true
}
```

---

### 7.6 Dashboard Stats (Admin)

#### `GET /api/v1/dashboard/admin` *(Admin only)*

**Response `200 OK`**
```json
{
  "total_requests": 24,
  "open_requests": 6,
  "pending_applications": 3,
  "pending_teachers": 2
}
```

---

### 7.7 Profile (Teacher)

#### `GET /api/v1/profile`

**Response `200 OK`**
```json
{
  "id": 5,
  "full_name": "Anna Müller",
  "personal_number": "T-0042",
  "email": "anna.mueller@edusub.ch",
  "phone": "0791234567",
  "bio": "Experienced primary school teacher.",
  "profile_picture": "/uploads/profile_pictures/user_5.jpg",
  "subjects": [
    { "id": 3, "name": "Mathematics" },
    { "id": 7, "name": "English" }
  ],
  "is_approved": true
}
```

#### `PATCH /api/v1/profile`

**Request**
```json
{
  "full_name": "Anna Müller-Schmidt",
  "phone": "0799876543",
  "bio": "Updated bio.",
  "subjects": [3, 5, 7]
}
```

**Response `200 OK`**
```json
{
  "id": 5,
  "full_name": "Anna Müller-Schmidt",
  "phone": "0799876543",
  "bio": "Updated bio.",
  "subjects": [
    { "id": 3, "name": "Mathematics" },
    { "id": 5, "name": "German" },
    { "id": 7, "name": "English" }
  ]
}
```

---

## 8. Wireframes

> Wireframe sketches will be provided as a separate PDF (`wireframes.pdf`) in this repository.

### Planned Screens

| Screen | Role | Description |
|--------|------|-------------|
| Login | All | Email + password form |
| Teacher Registration | Teacher | Name, email, phone, password, subject selection, document upload |
| Admin Dashboard | Admin | Stats overview (open requests, pending applications, pending teachers) |
| Substitute Requests List | Admin / Teacher | Full requests table with status badges; filter by level for teachers |
| Request Detail | Admin | Full request info + applicants list with approve button |
| Admin — Teacher List | Admin | All teachers with approval status and link to profile |
| Admin — Teacher Profile | Admin | Full teacher details, documents, approve/reject buttons |
| Teacher Dashboard — Available | Teacher | Open requests with grade/subject, date, time slot, expiry countdown, apply button |
| Teacher Dashboard — My Applications | Teacher | All own applications with pending / approved / rejected status + withdraw button |
| Teacher Profile | Teacher | Edit name, phone, bio, subjects; upload profile picture; change password; staff number display |

---

## 9. Data Models

### User

| Field | Type | Notes |
|-------|------|-------|
| id | int | Primary key |
| full_name | str | |
| personal_number | str | Auto-generated staff number |
| email | str | Unique |
| hashed_password | str | bcrypt |
| role | enum | `admin` / `teacher` |
| is_approved | bool | Teachers only; defaults to `false` |
| phone | str | Digits only |
| bio | str | Optional |
| profile_picture | str | Path to uploaded file |
| documents_path | str | Comma-separated paths to uploaded documents |
| created_at | datetime | |

### Subject

| Field | Type | Notes |
|-------|------|-------|
| id | int | Primary key |
| name | str | e.g. "Mathematics" |
| level | str | `kg` / `primary` |
| grades | str | e.g. "3-6", "KG" |

### UserSubject (junction)

| Field | Type | Notes |
|-------|------|-------|
| user_id | int | FK → User |
| subject_id | int | FK → Subject |

### SubstituteRequest

| Field | Type | Notes |
|-------|------|-------|
| id | int | Primary key |
| date | date | Coverage date |
| grade_level | str | e.g. "3a", "KG1" |
| subject_id | int | FK → Subject |
| time_slot | str | Optional, format HH:MM-HH:MM |
| note | str | Optional additional notes |
| status | enum | `open` / `filled` / `closed` |
| expires_at | datetime | Auto-calculated: 12h before assignment start |
| created_by | int | FK → User (admin) |
| created_at | datetime | |

### Application

| Field | Type | Notes |
|-------|------|-------|
| id | int | Primary key |
| request_id | int | FK → SubstituteRequest |
| teacher_id | int | FK → User |
| status | enum | `pending` / `approved` / `rejected` |
| applied_at | datetime | |

---

## 10. Project Structure (planned)

```
Web-based/
├── backend/
│   ├── main.py                   # FastAPI app, router registration
│   ├── database.py               # SQLite engine, session factory
│   ├── models/
│   │   ├── user.py
│   │   ├── request.py
│   │   ├── application.py
│   │   └── subject.py
│   ├── schemas/                  # Pydantic request/response schemas
│   │   ├── auth.py
│   │   ├── request.py
│   │   ├── application.py
│   │   ├── subject.py
│   │   └── user.py
│   ├── services/
│   │   ├── auth_service.py
│   │   ├── request_service.py
│   │   ├── application_service.py
│   │   └── profile_service.py
│   ├── routers/
│   │   ├── auth.py
│   │   ├── requests.py
│   │   ├── applications.py
│   │   ├── subjects.py
│   │   ├── teachers.py
│   │   ├── dashboard.py
│   │   └── profile.py
│   ├── core/
│   │   ├── security.py           # JWT creation & verification
│   │   └── dependencies.py       # get_current_user, require_admin
│   └── tests/
│       ├── test_auth.py
│       ├── test_requests.py
│       ├── test_applications.py
│       └── test_profile.py
│
├── frontend/
│   ├── index.html
│   ├── vite.config.ts
│   ├── src/
│   │   ├── main.tsx
│   │   ├── App.tsx
│   │   ├── api/                  # Axios client + endpoint functions
│   │   ├── components/           # Shared UI components
│   │   ├── pages/
│   │   │   ├── Login.tsx
│   │   │   ├── Register.tsx
│   │   │   ├── admin/
│   │   │   │   ├── Dashboard.tsx
│   │   │   │   ├── Requests.tsx
│   │   │   │   ├── RequestDetail.tsx
│   │   │   │   ├── Teachers.tsx
│   │   │   │   └── TeacherProfile.tsx
│   │   │   └── teacher/
│   │   │       ├── Dashboard.tsx
│   │   │       ├── MyApplications.tsx
│   │   │       └── Profile.tsx
│   │   └── store/                # Auth state (JWT, role)
│   └── public/
│
├── requirements.txt
├── package.json
└── README.md
```

