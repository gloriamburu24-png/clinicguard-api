from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from datetime import datetime
import os

from database.session import get_session, create_tables
from models.user import User, UserCreate, UserResponse
from models.patient import Patient, PatientCreate, PatientUpdate
from auth import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user,
    get_current_admin,
    get_current_doctor,
    get_receptionist_or_above
)

app = FastAPI(title="ClinicGuard API", version="1.0.0")

@app.on_event("startup")
def on_startup():
    """Create tables on application startup."""
    create_tables()

# ====== RATE LIMITING ======
if not os.getenv("DISABLE_RATE_LIMIT"):
    limiter = Limiter(key_func=get_remote_address)
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
else:
    class DummyLimiter:
        def limit(self, *args, **kwargs):
            def decorator(func):
                return func
            return decorator
    limiter = DummyLimiter()

# ====== PORTFOLIO PAGE ======

@app.get("/", response_class=HTMLResponse)
async def portfolio():
    """Portfolio homepage with links to all assignments."""
    html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>Student Portfolio - Backend Assignments</title>
    <style>
        body {
            font-family: 'Segoe UI', Arial, sans-serif;
            margin: 40px;
            background: #f5f5f5;
        }
        .container {
            max-width: 900px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }
        .student-info {
            background: #eaf2f8;
            padding: 15px;
            border-radius: 8px;
            margin: 20px 0;
        }
        .student-info strong {
            color: #2c3e50;
        }
        .admission {
            font-size: 1.2em;
            color: #2980b9;
            font-weight: bold;
        }
        .assignment {
            margin: 12px 0;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 8px;
            border-left: 4px solid #3498db;
            transition: all 0.3s ease;
        }
        .assignment:hover {
            background: #e8f4fd;
            transform: translateX(5px);
        }
        .assignment a {
            color: #0366d6;
            text-decoration: none;
            font-weight: 500;
            display: flex;
            align-items: center;
        }
        .assignment a:hover {
            text-decoration: underline;
        }
        .badge {
            display: inline-block;
            background: #3498db;
            color: white;
            padding: 2px 10px;
            border-radius: 12px;
            font-size: 0.8em;
            margin-right: 10px;
        }
        .lesson-topic {
            color: #7f8c8d;
            font-size: 0.9em;
            margin-left: 10px;
        }
        .footer {
            margin-top: 30px;
            text-align: center;
            color: #95a5a6;
            font-size: 0.9em;
            border-top: 1px solid #ecf0f1;
            padding-top: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Backend Development Portfolio</h1>
        <div class="student-info">
            <p><strong>Student Name:</strong> GLORIA MBURU</p>
            <p><strong>Admission Number:</strong> <span class="admission">C027-01-0873/2024</span></p>
            <p><strong>Email:</strong> gloria.mburu24@students.dkut.ac.ke</p>
        </div>

        <h2>Backend Assignments</h2>
        <p style="color: #7f8c8d; margin-bottom: 20px;">Click on any assignment to view the complete code on GitHub</p>

        <div class="assignment">
            <a href="https://github.com/gloriamburu24-png/healthtrack-api" target="_blank">
                <span class="badge">Lesson 1</span>
                <span>HTTP & Your First API</span>
                <span class="lesson-topic">— FastAPI + Uvicorn, HTTP Methods, Status Codes</span>
            </a>
        </div>

        <div class="assignment">
            <a href="https://github.com/gloriamburu24-png/clinicguard-api" target="_blank">
                <span class="badge">Lesson 2</span>
                <span>Docker - Packaging Your API</span>
                <span class="lesson-topic">— Containers, Dockerfiles, Docker Compose</span>
            </a>
        </div>

        <div class="assignment">
            <a href="https://github.com/gloriamburu24-png/library-api" target="_blank">
                <span class="badge">Lesson 3</span>
                <span>Routing, Parameters & Request Bodies</span>
                <span class="lesson-topic">— Path Parameters, Query Parameters, Pydantic Validation</span>
            </a>
        </div>

        <div class="assignment">
            <a href="https://github.com/gloriamburu24-png/bookstore-api" target="_blank">
                <span class="badge">Lesson 4</span>
                <span>PostgreSQL & SQLModel - Your First Database</span>
                <span class="lesson-topic">— ORM, Database Migrations, SQLModel</span>
            </a>
        </div>

        <div class="assignment">
            <a href="https://github.com/gloriamburu24-png/gighub-api" target="_blank">
                <span class="badge">Lesson 5</span>
                <span>CRUD Operations</span>
                <span class="lesson-topic">— Create, Read, Update, Delete with Error Handling</span>
            </a>
        </div>

        <div class="assignment">
            <a href="https://github.com/gloriamburu24-png/product-api" target="_blank">
                <span class="badge">Lesson 6</span>
                <span>Error Handling & Validation</span>
                <span class="lesson-topic">— HTTPException, Custom Validators, Global Handlers</span>
            </a>
        </div>

        <div class="assignment">
            <a href="https://github.com/gloriamburu24-png/healthtrack" target="_blank">
                <span class="badge">Lesson 7</span>
                <span>User Authentication - JWT & Password Hashing</span>
                <span class="lesson-topic">— JWT Tokens, bcrypt, Login/Register Endpoints</span>
            </a>
        </div>

        <div class="assignment">
            <a href="https://github.com/gloriamburu24-png/clinicguard-api" target="_blank">
                <span class="badge">Lesson 8</span>
                <span>Authorization & Rate Limiting</span>
                <span class="lesson-topic">— RBAC, Dependency Injection, Rate Limiting</span>
            </a>
        </div>

        <div class="assignment">
            <a href="https://github.com/gloriamburu24-png/sendit-api" target="_blank">
                <span class="badge">Lesson 9</span>
                <span>File Uploads & External APIs</span>
                <span class="lesson-topic">— File Validation, httpx, Environment Variables</span>
            </a>
        </div>

        <div class="assignment">
            <a href="https://github.com/gloriamburu24-png/clinicguard-api" target="_blank">
                <span class="badge">Lesson 10</span>
                <span>Testing & Deployment (Cloud)</span>
                <span class="lesson-topic">— Pytest, CI/CD, Render Deployment</span>
            </a>
        </div>

        <div class="footer">
            <p>Deployed on Render | Last Updated: August 2026</p>
            <p style="font-size: 0.8em;">Click on any assignment link to view the complete source code on GitHub</p>
        </div>
    </div>
</body>
</html>
    """
    return HTMLResponse(content=html_content)

# ====== AUTHENTICATION ENDPOINTS ======

@app.post("/register", status_code=201)
@limiter.limit("5/minute")
def register_user(
    request: Request,
    user_data: UserCreate,
    session: Session = Depends(get_session)
):
    """Register a new user."""
    existing = session.exec(select(User).where(User.username == user_data.username)).first()
    if existing:
        raise HTTPException(409, "Username already exists")

    existing = session.exec(select(User).where(User.email == user_data.email)).first()
    if existing:
        raise HTTPException(409, "Email already exists")

    hashed = hash_password(user_data.password)
    db_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed,
        full_name=user_data.full_name,
        role=user_data.role
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    return {"message": "User created successfully", "user": db_user}

@app.post("/login")
@limiter.limit("5/minute")
def login_user(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session)
):
    """Login and receive an access token."""
    user = session.exec(select(User).where(User.username == form_data.username)).first()
    if not user:
        raise HTTPException(401, "Invalid credentials")

    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(401, "Invalid credentials")

    if not user.is_active:
        raise HTTPException(403, "User is inactive")

    user.last_login = datetime.utcnow()
    session.commit()

    token = create_access_token({"sub": user.username})

    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": 30 * 60,
        "username": user.username,
        "role": user.role
    }

# ====== PATIENT ENDPOINTS ======

@app.post("/patients", status_code=201)
@limiter.limit("20/hour")
def create_patient(
    request: Request,
    patient_data: PatientCreate,
    current_user: User = Depends(get_receptionist_or_above),
    session: Session = Depends(get_session)
):
    """Create a new patient record."""
    if patient_data.doctor_id:
        doctor = session.get(User, patient_data.doctor_id)
        if not doctor:
            raise HTTPException(404, "Doctor not found")
        if doctor.role not in ["admin", "doctor"]:
            raise HTTPException(400, "Assigned user must be a doctor")

    db_patient = Patient(
        **patient_data.dict(),
        created_by=current_user.id
    )
    session.add(db_patient)
    session.commit()
    session.refresh(db_patient)
    return db_patient

@app.get("/patients")
@limiter.limit("30/minute")
def list_patients(
    request: Request,
    current_user: User = Depends(get_receptionist_or_above),
    session: Session = Depends(get_session)
):
    """List all patients."""
    query = select(Patient)

    if current_user.role == "doctor":
        query = query.where(Patient.doctor_id == current_user.id)

    return session.exec(query).all()

@app.get("/patients/{patient_id}")
@limiter.limit("30/minute")
def get_patient(
    request: Request,
    patient_id: int,
    current_user: User = Depends(get_receptionist_or_above),
    session: Session = Depends(get_session)
):
    """Get a specific patient record."""
    patient = session.get(Patient, patient_id)
    if not patient:
        raise HTTPException(404, "Patient not found")

    if current_user.role == "doctor" and patient.doctor_id != current_user.id:
        raise HTTPException(403, "Access denied to this patient record")

    return patient

@app.patch("/patients/{patient_id}")
@limiter.limit("20/minute")
def update_patient(
    request: Request,
    patient_id: int,
    patient_update: PatientUpdate,
    current_user: User = Depends(get_current_doctor),
    session: Session = Depends(get_session)
):
    """Update a patient record."""
    patient = session.get(Patient, patient_id)
    if not patient:
        raise HTTPException(404, "Patient not found")

    if current_user.role != "admin" and patient.doctor_id != current_user.id:
        raise HTTPException(403, "You can only update your own patients")

    for key, value in patient_update.dict(exclude_unset=True).items():
        setattr(patient, key, value)

    patient.updated_at = datetime.utcnow()
    session.commit()
    session.refresh(patient)
    return patient

@app.delete("/patients/{patient_id}")
def delete_patient(
    patient_id: int,
    admin: User = Depends(get_current_admin),
    session: Session = Depends(get_session)
):
    """Delete a patient record (admin only)."""
    patient = session.get(Patient, patient_id)
    if not patient:
        raise HTTPException(404, "Patient not found")

    session.delete(patient)
    session.commit()
    return {"message": "Patient record deleted"}

# ====== ADMIN ENDPOINTS ======

@app.get("/users", response_model=list[UserResponse])
def list_users(
    admin: User = Depends(get_current_admin),
    session: Session = Depends(get_session)
):
    """List all users (admin only)."""
    return session.exec(select(User)).all()

@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    admin: User = Depends(get_current_admin),
    session: Session = Depends(get_session)
):
    """Get a specific user (admin only)."""
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(404, "User not found")
    return user

@app.patch("/users/{user_id}/role")
def update_user_role(
    user_id: int,
    new_role: str,
    admin: User = Depends(get_current_admin),
    session: Session = Depends(get_session)
):
    """Update a user's role (admin only)."""
    if new_role not in ["admin", "doctor", "receptionist"]:
        raise HTTPException(400, "Invalid role")

    user = session.get(User, user_id)
    if not user:
        raise HTTPException(404, "User not found")

    if user.id == admin.id:
        raise HTTPException(400, "You cannot change your own role")

    user.role = new_role
    session.commit()
    return {"message": f"User {user.username} role updated to {new_role}"}

@app.patch("/users/{user_id}/activate")
def toggle_user_activation(
    user_id: int,
    activate: bool,
    admin: User = Depends(get_current_admin),
    session: Session = Depends(get_session)
):
    """Activate or deactivate a user (admin only)."""
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(404, "User not found")

    if user.id == admin.id:
        raise HTTPException(400, "You cannot deactivate yourself")

    user.is_active = activate
    session.commit()
    return {"message": f"User {user.username} activation set to {activate}"}

# ====== HEALTH CHECK ENDPOINT ======

@app.get("/health")
def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }