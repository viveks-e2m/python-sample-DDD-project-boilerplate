import pytest
from apps.user.domain.models import User
from apps.user.application.schema import UserCreateModel


class TestUserModel:
    """Test cases for User model"""
    
    def test_user_creation(self):
        """Test creating a user instance"""
        user = User(
            username="testuser",
            email="test@example.com",
            password="password",
            first_name="Test",
            last_name="User"
        )
        
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.password == "password"
        assert user.first_name == "Test"
        assert user.last_name == "User"
        assert user.is_active is True
        assert user.is_superuser is False
    
    def test_set_password(self):
        """Test setting a user's password"""
        user = User(
            username="testuser",
            email="test@example.com",
            password="",
            first_name="Test",
            last_name="User"
        )
        
        user.set_password("Test1234")
        assert user.password != ""
        assert len(user.password) > 0
    
    def test_check_password(self):
        """Test checking a user's password"""
        user = User(
            username="testuser",
            email="test@example.com",
            password="",
            first_name="Test",
            last_name="User"
        )
        
        user.set_password("Test1234")
        assert user.check_password("Test1234") is True
        assert user.check_password("WrongPassword") is False