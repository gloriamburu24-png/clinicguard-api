import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Tell the app we're running tests
os.environ["PYTEST_RUNNING"] = "1"
os.environ["DISABLE_RATE_LIMIT"] = "1"
os.environ["DATABASE_URL"] = "sqlite:///./test.db"

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from main import app, get_session  # <--- IMPORT get_session HERE

TEST_DATABASE_URL = "sqlite:///./test.db"

@pytest.fixture(scope="function")
def client():
    """Create a test client for the FastAPI app."""
    
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
    
    def get_test_session():
        with Session(engine) as session:
            yield session
    
    # Override the dependency with our test session
    app.dependency_overrides[get_session] = get_test_session
    
    yield TestClient(app)
    
    app.dependency_overrides.clear()

@pytest.fixture
def test_user():
    """Create a test user for authentication tests."""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123",
        "full_name": "Test User",
        "role": "admin"
    }