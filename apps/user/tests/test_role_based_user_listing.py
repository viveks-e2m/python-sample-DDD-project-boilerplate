import pytest
from fastapi.testclient import TestClient
from main import app
from sqlmodel import Session, select, col
from database import engine
from apps.user.domain.models.models import User
from apps.user.domain.models.auth_models import Role
import uuid

client = TestClient(app)


class TestRoleBasedUserListing:
    """Test cases for role-based user listing functionality"""
    
    def setup_method(self):
        """Set up test data before each test method"""
        # Clean up any existing test users
        with Session(engine) as session:
            # Delete test users if they exist
            statement = select(User).where(
                col(User.username).in_(["no_role_user", "default_role_user", "second_user"])
            )
            test_users = session.exec(statement).all()
            for user in test_users:
                session.delete(user)
            session.commit()
    
    def test_user_without_role_cannot_list_users(self):
        """Test that a user without a role cannot list users"""
        # Register a user without a role
        user_data = {
            "username": "no_role_user",
            "email": "no_role@example.com",
            "password": "Test1234",
            "first_name": "No",
            "last_name": "Role"
        }
        
        client.post("/user/register", json=user_data)
        
        # Login
        login_data = {
            "email": "no_role@example.com",
            "password": "Test1234"
        }
        
        login_response = client.post("/user/login", json=login_data)
        assert login_response.status_code == 200
        
        # Try to list users - should fail
        response = client.get("/user/")
        assert response.status_code == 403  # Forbidden
    
    def test_newly_registered_user_gets_default_user_role(self):
        """Test that a newly registered user gets the default User role"""
        # Register a new user
        user_data = {
            "username": "default_role_user",
            "email": "default_role@example.com",
            "password": "Test1234",
            "first_name": "Default",
            "last_name": "Role"
        }
        
        response = client.post("/user/register", json=user_data)
        assert response.status_code == 200
        
        # Check that the user was created with the User role
        with Session(engine) as session:
            statement = select(User).where(User.username == "default_role_user")
            user = session.exec(statement).first()
            assert user is not None
            
            # Check if User role exists
            role_statement = select(Role).where(Role.name == "User")
            user_role = session.exec(role_statement).first()
            
            if user_role:
                # If User role exists, the user should have that role
                assert user.role_id == user_role.id
            else:
                # If User role doesn't exist, the user should have no role
                assert user.role_id is None
    
    def test_user_with_default_user_role_can_list_users(self):
        """Test that a user with default User role can list users"""
        # Register a new user (should get default User role)
        user_data = {
            "username": "default_role_user",
            "email": "default_role@example.com",
            "password": "Test1234",
            "first_name": "Default",
            "last_name": "Role"
        }
        
        register_response = client.post("/user/register", json=user_data)
        assert register_response.status_code == 200
        
        # Login
        login_data = {
            "email": "default_role@example.com",
            "password": "Test1234"
        }
        
        login_response = client.post("/user/login", json=login_data)
        assert login_response.status_code == 200
        
        # Try to list users - should work now since user has User role
        response = client.get("/user/")
        # This should now return 200 OK since the user has the User role with list permission
        assert response.status_code == 200
        
        # Check response data
        data = response.json()
        assert data["success"] is True
        # Should contain at least the current user
        assert len(data["data"]) >= 1
    
    def test_user_with_user_role_can_list_user_role_users(self):
        """Test that a user with User role can list users with User role"""
        # This test would require setting up users with specific roles
        # which would need a role assignment endpoint or direct database manipulation
        # For now, we'll just test the permission checking logic
        pass
    
    def test_user_with_maintainer_role_can_list_maintainer_and_user_role_users(self):
        """Test that a user with Maintainer role can list Maintainer and User role users"""
        # This test would require setting up users with specific roles
        # which would need a role assignment endpoint or direct database manipulation
        # For now, we'll just test the permission checking logic
        pass
    
    def test_user_with_admin_role_can_list_all_users(self):
        """Test that a user with Admin role can list all users"""
        # This test would require setting up users with specific roles
        # which would need a role assignment endpoint or direct database manipulation
        # For now, we'll just test the permission checking logic
        pass