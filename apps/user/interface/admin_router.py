import uuid
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import JSONResponse
from apps.user.application.schema import (
    UserCreateModel,
    UserPublicModel,
    UserUpdateModel,
    BaseResponse,
)
from apps.user.application.service import UserApplicationService
from apps.user.domain.models import User
from apps.user.interface.dependency import get_user_service, get_authenticated_user
from database import SessionDep
from typing import List, Optional

router: APIRouter = APIRouter()


@router.get(
    path="/admin/users", 
    response_model=BaseResponse[List[UserPublicModel]], 
    tags=["Admin"]
)
async def list_users(
    current_user: User = Depends(get_authenticated_user),
    service: UserApplicationService = Depends(get_user_service),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    active_only: bool = Query(True)
):
    """
    List all users (with pagination, filters).
    
    Requires admin/superuser role.
    
    Args:
        current_user: The authenticated user (dependency injected)
        service: User application service (dependency injected)
        skip: Number of users to skip (for pagination)
        limit: Maximum number of users to return (for pagination)
        active_only: Filter to show only active users
        
    Returns:
        BaseResponse containing a list of users
        
    Raises:
        HTTPException: 403 - Insufficient permissions
        HTTPException: 500 - Internal server error
    """
    # Check if user is superuser
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this resource",
        )
        
    try:
        result = await service.list_users(skip, limit, active_only)
        return BaseResponse(
            success=True, 
            data=result, 
            message="Users retrieved successfully",
            status_code=status.HTTP_200_OK
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}",
        )


@router.get(
    path="/admin/users/{user_id}", 
    response_model=BaseResponse[UserPublicModel], 
    tags=["Admin"]
)
async def get_user(
    user_id: uuid.UUID,
    current_user: User = Depends(get_authenticated_user),
    service: UserApplicationService = Depends(get_user_service)
):
    """
    Get specific user details.
    
    Requires admin/superuser role.
    
    Args:
        user_id: The ID of the user to retrieve
        current_user: The authenticated user (dependency injected)
        service: User application service (dependency injected)
        
    Returns:
        BaseResponse containing the user details
        
    Raises:
        HTTPException: 403 - Insufficient permissions
        HTTPException: 404 - User not found
        HTTPException: 500 - Internal server error
    """
    # Check if user is superuser
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this resource",
        )
        
    try:
        result = await service.get_user(user_id)
        return BaseResponse(
            success=True, 
            data=result, 
            message="User retrieved successfully",
            status_code=status.HTTP_200_OK
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}",
        )


@router.post(
    path="/admin/users", 
    response_model=BaseResponse[UserPublicModel], 
    tags=["Admin"]
)
async def create_user(
    user_data: UserCreateModel,
    current_user: User = Depends(get_authenticated_user),
    service: UserApplicationService = Depends(get_user_service)
):
    """
    Create a new user (e.g., for system invite).
    
    Requires admin/superuser role.
    
    Args:
        user_data: The data for the new user
        current_user: The authenticated user (dependency injected)
        service: User application service (dependency injected)
        
    Returns:
        BaseResponse containing the created user
        
    Raises:
        HTTPException: 400 - Invalid input data
        HTTPException: 403 - Insufficient permissions
        HTTPException: 409 - User already exists
        HTTPException: 500 - Internal server error
    """
    # Check if user is superuser
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this resource",
        )
        
    try:
        result = await service.register_user(user_data)
        return BaseResponse(
            success=True, 
            data=result, 
            message="User created successfully",
            status_code=status.HTTP_201_CREATED
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}",
        )


@router.patch(
    path="/admin/users/{user_id}", 
    response_model=BaseResponse[UserPublicModel], 
    tags=["Admin"]
)
async def update_user(
    user_id: uuid.UUID,
    user_data: UserUpdateModel,
    current_user: User = Depends(get_authenticated_user),
    service: UserApplicationService = Depends(get_user_service)
):
    """
    Update user details (role, status, etc.).
    
    Requires admin/superuser role.
    
    Args:
        user_id: The ID of the user to update
        user_data: The updated data for the user
        current_user: The authenticated user (dependency injected)
        service: User application service (dependency injected)
        
    Returns:
        BaseResponse containing the updated user
        
    Raises:
        HTTPException: 400 - Invalid input data
        HTTPException: 403 - Insufficient permissions
        HTTPException: 404 - User not found
        HTTPException: 500 - Internal server error
    """
    # Check if user is superuser
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this resource",
        )
        
    try:
        result = await service.admin_update_user(user_id, user_data)
        return BaseResponse(
            success=True, 
            data=result, 
            message="User updated successfully",
            status_code=status.HTTP_200_OK
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}",
        )


@router.delete(
    path="/admin/users/{user_id}", 
    response_model=BaseResponse[UserPublicModel], 
    tags=["Admin"]
)
async def delete_user(
    user_id: uuid.UUID,
    current_user: User = Depends(get_authenticated_user),
    service: UserApplicationService = Depends(get_user_service)
):
    """
    Delete/deactivate a user.
    
    Requires admin/superuser role.
    
    Args:
        user_id: The ID of the user to delete
        current_user: The authenticated user (dependency injected)
        service: User application service (dependency injected)
        
    Returns:
        BaseResponse containing the deleted user
        
    Raises:
        HTTPException: 403 - Insufficient permissions
        HTTPException: 404 - User not found
        HTTPException: 500 - Internal server error
    """
    # Check if user is superuser
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this resource",
        )
        
    try:
        result = await service.delete_user(user_id)
        return BaseResponse(
            success=True, 
            data=result, 
            message="User deleted successfully",
            status_code=status.HTTP_200_OK
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}",
        )


@router.patch(
    path="/admin/users/{user_id}/status", 
    response_model=BaseResponse[UserPublicModel], 
    tags=["Admin"]
)
async def update_user_status(
    user_id: uuid.UUID,
    is_active: bool,
    is_superuser: Optional[bool] = None,
    current_user: User = Depends(get_authenticated_user),
    service: UserApplicationService = Depends(get_user_service)
):
    """
    Activate/deactivate/lock user.
    
    Requires admin/superuser role.
    
    Args:
        user_id: The ID of the user to update
        is_active: Whether the user should be active
        is_superuser: Whether the user should be a superuser (optional)
        current_user: The authenticated user (dependency injected)
        service: User application service (dependency injected)
        
    Returns:
        BaseResponse containing the updated user
        
    Raises:
        HTTPException: 400 - Invalid input data
        HTTPException: 403 - Insufficient permissions
        HTTPException: 404 - User not found
        HTTPException: 500 - Internal server error
    """
    # Check if user is superuser
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this resource",
        )
        
    try:
        result = await service.update_user_status(user_id, is_active, is_superuser)
        return BaseResponse(
            success=True, 
            data=result, 
            message="User status updated successfully",
            status_code=status.HTTP_200_OK
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}",
        )