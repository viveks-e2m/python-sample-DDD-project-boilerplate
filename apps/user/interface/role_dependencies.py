"""
Dependency functions for role-based access control in FastAPI routes
"""

from fastapi import Depends, HTTPException, status
from apps.user.domain.services.role_service import RoleService
from apps.user.domain.models.models import User
from apps.user.interface.dependency import get_authenticated_user
from database import get_session
from sqlmodel import Session


def get_role_service(session: Session = Depends(get_session)):
    """
    Dependency to get RoleService instance
    """
    return RoleService(session)


def require_role(required_role: str):
    """
    Dependency to require a specific role for access
    
    Usage:
    @router.get("/admin-only")
    def admin_only_route(user=Depends(require_role("Admin"))):
        return {"message": "Admin access granted"}
    """
    def role_checker(
        current_user: User = Depends(get_authenticated_user),
        role_service: RoleService = Depends(get_role_service)
    ):
        if not role_service.user_has_role(current_user, required_role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role: {required_role}"
            )
        return current_user
    return role_checker


def require_permission(required_permission: str):
    """
    Dependency to require a specific permission for access
    
    Usage:
    @router.get("/manage-users")
    def manage_users_route(user=Depends(require_permission("manage_users"))):
        return {"message": "Permission granted"}
    """
    def permission_checker(
        current_user: User = Depends(get_authenticated_user),
        role_service: RoleService = Depends(get_role_service)
    ):
        if not role_service.user_has_permission(current_user, required_permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required permission: {required_permission}"
            )
        return current_user
    return permission_checker


def require_any_permission(required_permissions: list[str]):
    """
    Dependency to require any of the specified permissions for access
    
    Usage:
    @router.get("/admin-dashboard")
    def admin_dashboard(user=Depends(require_any_permission(["manage_users", "view_admin_dashboard"]))):
        return {"message": "Access granted"}
    """
    def permission_checker(
        current_user: User = Depends(get_authenticated_user),
        role_service: RoleService = Depends(get_role_service)
    ):
        if not role_service.user_has_any_permission(current_user, required_permissions):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required permissions: {required_permissions}"
            )
        return current_user
    return permission_checker


def require_all_permissions(required_permissions: list[str]):
    """
    Dependency to require all of the specified permissions for access
    
    Usage:
    @router.get("/user-profile")
    def user_profile(user=Depends(require_all_permissions(["view_profile", "edit_profile"]))):
        return {"message": "Access granted"}
    """
    def permission_checker(
        current_user: User = Depends(get_authenticated_user),
        role_service: RoleService = Depends(get_role_service)
    ):
        if not role_service.user_has_all_permissions(current_user, required_permissions):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required permissions: {required_permissions}"
            )
        return current_user
    return permission_checker