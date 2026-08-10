import pytest
from datetime import datetime
from tests.conftest import client, test_user

@pytest.fixture
def auth_headers(client, test_user):
    """Get authentication headers for protected endpoints."""
    # Register user
    client.post("/register", json=test_user)
    
    # Login
    response = client.post(
        "/login",
        data={"username": test_user["username"], "password": test_user["password"]}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_create_patient(client, auth_headers):
    """Test creating a patient."""
    patient_data = {
        "first_name": "Jane",
        "last_name": "Muthoni",
        "date_of_birth": "1990-05-15T00:00:00",
        "phone": "0712345678",
        "email": "jane@example.com",
        "address": "Nairobi, Kenya",
        "medical_notes": "Regular checkup",
        "doctor_id": None
    }
    
    response = client.post("/patients", json=patient_data, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["first_name"] == patient_data["first_name"]
    assert data["last_name"] == patient_data["last_name"]

def test_list_patients(client, auth_headers):
    """Test listing patients."""
    # Create a patient first
    patient_data = {
        "first_name": "Jane",
        "last_name": "Muthoni",
        "date_of_birth": "1990-05-15T00:00:00",
        "phone": "0712345678",
        "email": "jane@example.com",
        "address": "Nairobi, Kenya",
        "medical_notes": "Regular checkup",
        "doctor_id": None
    }
    client.post("/patients", json=patient_data, headers=auth_headers)
    
    # List patients
    response = client.get("/patients", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["first_name"] == patient_data["first_name"]

def test_get_patient(client, auth_headers):
    """Test getting a single patient."""
    # Create a patient
    patient_data = {
        "first_name": "Jane",
        "last_name": "Muthoni",
        "date_of_birth": "1990-05-15T00:00:00",
        "phone": "0712345678",
        "email": "jane@example.com",
        "address": "Nairobi, Kenya",
        "medical_notes": "Regular checkup",
        "doctor_id": None
    }
    create_response = client.post("/patients", json=patient_data, headers=auth_headers)
    patient_id = create_response.json()["id"]
    
    # Get the patient
    response = client.get(f"/patients/{patient_id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["first_name"] == patient_data["first_name"]

def test_get_patient_not_found(client, auth_headers):
    """Test getting a non-existent patient."""
    response = client.get("/patients/99999", headers=auth_headers)
    assert response.status_code == 404

def test_update_patient(client, auth_headers):
    """Test updating a patient."""
    # Create a patient
    patient_data = {
        "first_name": "Jane",
        "last_name": "Muthoni",
        "date_of_birth": "1990-05-15T00:00:00",
        "phone": "0712345678",
        "email": "jane@example.com",
        "address": "Nairobi, Kenya",
        "medical_notes": "Regular checkup",
        "doctor_id": None
    }
    create_response = client.post("/patients", json=patient_data, headers=auth_headers)
    patient_id = create_response.json()["id"]
    
    # Update the patient
    update_data = {
        "first_name": "Updated",
        "medical_notes": "Updated notes"
    }
    response = client.patch(f"/patients/{patient_id}", json=update_data, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["first_name"] == "Updated"

def test_delete_patient(client, auth_headers):
    """Test deleting a patient (admin only)."""
    # Create a patient
    patient_data = {
        "first_name": "Jane",
        "last_name": "Muthoni",
        "date_of_birth": "1990-05-15T00:00:00",
        "phone": "0712345678",
        "email": "jane@example.com",
        "address": "Nairobi, Kenya",
        "medical_notes": "Regular checkup",
        "doctor_id": None
    }
    create_response = client.post("/patients", json=patient_data, headers=auth_headers)
    patient_id = create_response.json()["id"]
    
    # Delete the patient
    response = client.delete(f"/patients/{patient_id}", headers=auth_headers)
    assert response.status_code == 200
    
    # Verify deletion
    response = client.get(f"/patients/{patient_id}", headers=auth_headers)
    assert response.status_code == 404