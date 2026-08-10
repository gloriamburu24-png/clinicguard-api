import pytest
from tests.conftest import client, test_user

@pytest.fixture
def auth_headers(client, test_user):
    """Get authentication headers for protected endpoints."""
    client.post("/register", json=test_user)
    response = client.post(
        "/login",
        data={"username": test_user["username"], "password": test_user["password"]}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_404_error(client):
    """Test 404 error handling."""
    response = client.get("/non-existent-endpoint")
    assert response.status_code == 404

def test_validation_error(client, auth_headers):
    """Test validation error handling."""
    # Create a patient with invalid data
    patient_data = {
        "first_name": "",  # Empty name should fail
        "last_name": "",   # Empty name should fail
        "date_of_birth": "1990-05-15T00:00:00",
        "phone": "",       # Empty phone should fail
        "email": "invalid-email",  # Invalid email format
        "address": "Nairobi, Kenya",
        "medical_notes": "Regular checkup",
        "doctor_id": None
    }
    response = client.post("/patients", json=patient_data, headers=auth_headers)
    assert response.status_code in [400, 422]

def test_unauthorized_access(client):
    """Test unauthorized access to protected endpoints."""
    response = client.get("/patients")
    assert response.status_code == 401  # Unauthorized