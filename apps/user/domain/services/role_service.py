import uuid
from uuid import UUID
from typing import List, Optional
from sqlmodel import select, col
from apps.user.domain.models.auth_models import Role, Permission, RolePermission
from apps.user.domain.models.models import User
from database import Session


class RoleService:
    """
    Service for handling role and permission operations
    """

    def __init__(self, session: Session):
        self.session = session

    def get_user_role(self, user: User) -> Optional[Role]:
        """
        Get the role of a user
        
        Args:
            user: The user object
            
        Returns:
            The role object or None if user has no role or user is superuser
        """
        # If user is superuser, they have all permissions
        if user.is_superuser:
            return None  # Superuser has all permissions by default
            
        # If user has no role_id, they have no specific role
        if not user.role_id:
            return None
            
        # Get the role - ensure we're working with a proper UUID object
        from uuid import UUID
        role_id = user.role_id if isinstance(user.role_id, UUID) else UUID(user.role_id) if user.role_id else None
        if not role_id:
            return None
            
        # Get the role from database
        return self.session.get(Role, role_id)

    def get_user_permissions(self, user: User) -> List[Permission]:
        """
        Get all permissions for a user
        
        Args:
            user: The user object
            
        Returns:
            List of permission objects
        """
        # If user is superuser, they have all permissions
        if user.is_superuser:
            statement = select(Permission)
            result = self.session.exec(statement)
            return list(result.all())
            
        # If user has no role, they have no permissions
        if not user.role_id:
            return []
            
        # Get the role - ensure we're working with a proper UUID object
        from uuid import UUID
        role_id = user.role_id if isinstance(user.role_id, UUID) else UUID(user.role_id) if user.role_id else None
        if not role_id:
            return []
            
        role = self.session.get(Role, role_id)
        if not role:
            return []
            
        # Get all permissions for this role
        statement = select(Permission).join(
            RolePermission
        ).where(RolePermission.role_id == role.id, RolePermission.permission_id == Permission.id)
        
        result = self.session.exec(statement)
        return list(result.all())

    def user_has_role(self, user: User, role_name: str) -> bool:
        """
        Check if user has a specific role
        
        Args:
            user: The user object
            role_name: The name of the role to check
            
        Returns:
            True if user has the role, False otherwise
        """
        # If user is superuser, they have all roles
        if user.is_superuser:
            return True
            
        # If user has no role_id, they don't have the specific role
        if not user.role_id:
            return False
            
        # Get the role - ensure we're working with a proper UUID object
        from uuid import UUID
        role_id = user.role_id if isinstance(user.role_id, UUID) else UUID(user.role_id) if user.role_id else None
        if not role_id:
            return False
            
        role = self.session.get(Role, role_id)
        if not role:
            return False
            
        return role.name == role_name

    def user_has_permission(self, user: User, permission_name: str) -> bool:
        """
        Check if user has a specific permission
        
        Args:
            user: The user object
            permission_name: The name of the permission to check
            
        Returns:
            True if user has the permission, False otherwise
        """
        # If user is superuser, they have all permissions
        if user.is_superuser:
            return True
            
        # If user has no role, they don't have any permissions
        if not user.role_id:
            return False
            
        # Get the role - ensure we're working with a proper UUID object
        role_id = user.role_id if isinstance(user.role_id, UUID) else UUID(user.role_id) if user.role_id else None
        if not role_id:
            return False
            
        role = self.session.get(Role, role_id)
        if not role:
            return False
            
        # Check if the permission exists for this role
        statement = select(Permission).join(
            RolePermission
        ).where(
            RolePermission.role_id == role.id,
            RolePermission.permission_id == Permission.id,
            Permission.name == permission_name
        )
        
        result = self.session.exec(statement)
        return result.first() is not None

    def user_has_any_permission(self, user: User, permission_names: List[str]) -> bool:
        """
        Check if user has any of the specified permissions
        
        Args:
            user: The user object
            permission_names: List of permission names to check
            
        Returns:
            True if user has any of the permissions, False otherwise
        """
        # If user is superuser, they have all permissions
        if user.is_superuser:
            return True
        # If user has no role, they don't have any permissions
        if not user.role_id:
            return False
        
        # Get the role - ensure we're working with a proper UUID object
        from uuid import UUID
        role_id = user.role_id if isinstance(user.role_id, UUID) else UUID(user.role_id) if user.role_id else None
        if not role_id:
            return False
            
        role = self.session.get(Role, role_id)
        if not role:
            return False
            
        # Check if any of the permissions exist for this role
        statement = select(Permission).join(
            RolePermission
        ).where(
            RolePermission.role_id == role.id,
            RolePermission.permission_id == Permission.id
        )
        # Add the IN clause manually
        if permission_names:
            statement = statement.where(col(Permission.name).in_(permission_names))
        
        result = self.session.exec(statement)
        return result.first() is not None

    def user_has_all_permissions(self, user: User, permission_names: List[str]) -> bool:
        """
        Check if user has all of the specified permissions
        
        Args:
            user: The user object
            permission_names: List of permission names to check
            
        Returns:
            True if user has all of the permissions, False otherwise
        """
        # If user is superuser, they have all permissions
        if user.is_superuser:
            return True
            
        # If user has no role, they don't have any permissions
        if not user.role_id:
            return False
            
        # Get the role - ensure we're working with a proper UUID object
        from uuid import UUID
        role_id: UUID | None = user.role_id if isinstance(user.role_id, UUID) else UUID(user.role_id) if user.role_id else None
        if not role_id:
            return False
            
        role: Role | None = self.session.get(Role, role_id)
        if not role:
            return False
            
        # Count how many of the required permissions the user has
        statement = select(Permission).join(
            RolePermission
        ).where(
            RolePermission.role_id == role.id,
            RolePermission.permission_id == Permission.id
        )
        
        # Add the IN clause manually
        if permission_names:
            statement = statement.where(col(Permission.name).in_(permission_names))
        
        result = self.session.exec(statement)
        user_permissions = list(result.all())
        
        # User has all permissions if the count matches the required permissions
        return len(user_permissions) == len(permission_names)