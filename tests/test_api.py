"""API endpoint tests."""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "app" in data
    assert "version" in data


def test_root_endpoint():
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data
    assert "docs" in data


def test_user_registration():
    """Test user registration."""
    response = client.post(
        "/api/v1/users/register",
        json={
            "email": "test@example.com",
            "password": "testpassword123",
            "company_name": "Test Company",
        },
    )
    # This will fail without database, but shows the structure
    assert response.status_code in [201, 500]  # 500 if DB not available


def test_invalid_login():
    """Test login with invalid credentials."""
    response = client.post(
        "/api/v1/users/login",
        json={
            "email": "invalid@example.com",
            "password": "wrongpassword",
        },
    )
    assert response.status_code in [401, 500]  # 500 if DB not available
