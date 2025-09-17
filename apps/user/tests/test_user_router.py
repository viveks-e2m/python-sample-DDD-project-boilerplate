import pytest
from fastapi.testclient import TestClient
from main import app
from apps.user.application.schema import UserCreateModel, UserLoginModel

client = TestClient(app)


class TestUserRouter:
    """Test cases for User router"""
    
    def test_register_user(self):
        """Test registering a user via API"""
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "Test1234",
            "first_name": "Test",
            "last_name": "User"
        }
        
        response = client.post("/user/register", json=user_data)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["username"] == "testuser"
        assert data["data"]["email"] == "test@example.com"
    
    def test_register_user_invalid_data(self):
        """Test registering a user with invalid data"""
        user_data = {
            "username": "testuser",
            "email": "invalid-email",
            "password": "123",
            "first_name": "Test",
            "last_name": "User"
        }
        
        response = client.post("/user/register", json=user_data)
        assert response.status_code == 422  # Validation error
    
    def test_login_user_with_cookie(self):
        """Test logging in a user via API and check for cookie"""
        # First register a user
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "Test1234",
            "first_name": "Test",
            "last_name": "User"
        }
        
        client.post("/user/register", json=user_data)
        
        # Then login
        login_data = {
            "username": "testuser",
            "password": "Test1234"
        }
        
        response = client.post("/user/login", json=login_data)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["username"] == "testuser"
        
        # Check that the access_token cookie is set
        assert "access_token" in response.cookies
        assert response.cookies["access_token"] is not None
    
    def test_login_user_wrong_credentials(self):
        """Test logging in with wrong credentials"""
        login_data = {
            "username": "testuser",
            "password": "WrongPassword"
        }
        
        response = client.post("/user/login", json=login_data)
        assert response.status_code == 401  # Unauthorized
    
    def test_logout_user(self):
        """Test logging out a user"""
        # First register and login a user
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "Test1234",
            "first_name": "Test",
            "last_name": "User"
        }
        
        client.post("/user/register", json=user_data)
        
        login_data = {
            "username": "testuser",
            "password": "Test1234"
        }
        
        # Login to get the cookie
        login_response = client.post("/user/login", json=login_data)
        assert login_response.status_code == 200
        
        # Logout
        response = client.post("/user/logout")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "User logged out successfully"
    
    def test_get_current_user_info(self):
        """Test getting current user info with cookie authentication"""
        # First register and login a user
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "Test1234",
            "first_name": "Test",
            "last_name": "User"
        }
        
        client.post("/user/register", json=user_data)
        
        login_data = {
            "username": "testuser",
            "password": "Test1234"
        }
        
        # Login to get the cookie
        login_response = client.post("/user/login", json=login_data)
        assert login_response.status_code == 200
        
        # Get current user info
        response = client.get("/user/me")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["username"] == "testuser"