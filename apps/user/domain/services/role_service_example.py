"""
Example of how to use the RoleService for role-based access control
"""

from apps.user.domain.services.role_service import RoleService
from apps.user.domain.models.models import User
from database import get_session


def example_role_check():
    """
    Example of how to check roles and permissions using RoleService
    """
    # Get a database session
    session = next(get_session())
    
    # Create the role service
    role_service = RoleService(session)
    
    # Assume we have a user (this would come from authentication)
    # user = get_current_user()  # This would be your authenticated user
    
    # Example 1: Check if user has a specific role
    # if role_service.user_has_role(user, "Admin"):
    #     # Allow access to admin features
    #     pass
    
    # Example 2: Check if user has a specific permission
    # if role_service.user_has_permission(user, "manage_users"):
    #     # Allow user management
    #     pass
    
    # Example 3: Check if user has any of several permissions
    # if role_service.user_has_any_permission(user, ["manage_users", "view_admin_dashboard"]):
    #     # Allow access to admin area
    #     pass
    
    # Example 4: Check if user has all required permissions
    # if role_service.user_has_all_permissions(user, ["view_profile", "edit_profile"]):
    #     # Allow profile editing
    #     pass
    
    # Example 5: Get all user permissions
    # permissions = role_service.get_user_permissions(user)
    # permission_names = [p.name for p in permissions]
    
    session.close()


# In your route handlers, you would use it like this:
#
# def protected_route(current_user: User = Depends(get_authenticated_user)):
#     session = next(get_session())
#     role_service = RoleService(session)
#     
#     if not role_service.user_has_permission(current_user, "view_admin_dashboard"):
#         raise HTTPException(status_code=403, detail="Forbidden")
#     
#     session.close()
#     return {"message": "Access granted"}