"""
Basic tests for the RoleService functionality
"""

import pytest
from unittest.mock import Mock, MagicMock
from apps.user.domain.services.role_service import RoleService
from apps.user.domain.models.auth_models import Role, Permission
from apps.user.domain.models.models import User


class TestRoleServiceBasic:
    """Basic test cases for RoleService"""

    def test_user_has_role_returns_true_for_superuser(self):
        """Test that superuser has any role"""
        # Arrange
        session = Mock()
        role_service = RoleService(session)
        user = User(username="admin", email="admin@test.com", first_name="Admin", 
                   last_name="User", password="hashed_password", is_superuser=True, role_id=None)
        
        # Act
        result = role_service.user_has_role(user, "Admin")
        
        # Assert
        assert result is True

    def test_user_has_permission_returns_true_for_superuser(self):
        """Test that superuser has any permission"""
        # Arrange
        session = Mock()
        role_service = RoleService(session)
        user = User(username="admin", email="admin@test.com", first_name="Admin", 
                   last_name="User", password="hashed_password", is_superuser=True, role_id=None)
        
        # Act
        result = role_service.user_has_permission(user, "manage_users")
        
        # Assert
        assert result is True

    def test_user_has_role_returns_false_for_user_without_role(self):
        """Test that user without role doesn't have specific role"""
        # Arrange
        session = Mock()
        role_service = RoleService(session)
        user = User(username="user", email="user@test.com", first_name="Regular", 
                   last_name="User", password="hashed_password", is_superuser=False, role_id=None)
        
        # Act
        result = role_service.user_has_role(user, "Admin")
        
        # Assert
        assert result is False

    def test_user_has_permission_returns_false_for_user_without_role(self):
        """Test that user without role doesn't have specific permission"""
        # Arrange
        session = Mock()
        role_service = RoleService(session)
        user = User(username="user", email="user@test.com", first_name="Regular", 
                   last_name="User", password="hashed_password", is_superuser=False, role_id=None)
        
        # Act
        result = role_service.user_has_permission(user, "manage_users")
        
        # Assert
        assert result is False