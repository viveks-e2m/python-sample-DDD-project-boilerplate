import uuid
from fastapi.routing import APIRouter
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Path,
    Query,
    status,
    Request,
    Response,
)
from apps.user.application.schema import (
    UserCreateModel,
    UserPublicModel,
    UserUpdateModel,
    UserLoginModel,
    UserPasswordResetModel,
    BaseResponse,
)
from apps.user.application.service import UserApplicationService
from apps.user.utils import (
    get_current_user,
    get_current_user_from_cookie,
    set_auth_cookie,
    clear_auth_cookie,
    create_access_token,
)
from apps.user.domain.models import User
from database import SessionDep
from typing import List, Optional

router: APIRouter = APIRouter()


@router.post(
    path="/register", response_model=BaseResponse[UserPublicModel], tags=["User"]
)
async def register_user(
    user_data: UserCreateModel, session: SessionDep
) -> BaseResponse[User]:
    """
    Register a new user.

    Creates a new user account with the provided data.

    Args:
        user_data: The data for the new user
        session: Database session dependency

    Returns:
        BaseResponse containing the created user

    Raises:
        HTTPException: 400 - Invalid input data
        HTTPException: 409 - User already exists
        HTTPException: 500 - Internal server error
    """
    try:
        service: UserApplicationService = UserApplicationService(session)
        result: User = await service.register_user(user_data)
        return BaseResponse(
            success=True, data=result, message="User registered successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}",
        )


@router.post(path="/login", response_model=BaseResponse[UserPublicModel], tags=["User"])
async def login_user(
    response: Response, login_data: UserLoginModel, session: SessionDep
) -> BaseResponse[User]:
    """
    Authenticate a user.

    Authenticates a user with the provided credentials.

    Args:
        response: FastAPI response object for setting cookies
        login_data: The login credentials
        session: Database session dependency

    Returns:
        BaseResponse containing the authenticated user

    Raises:
        HTTPException: 400 - Invalid credentials
        HTTPException: 401 - Authentication failed
        HTTPException: 404 - User not found
        HTTPException: 500 - Internal server error
    """
    try:
        service: UserApplicationService = UserApplicationService(session)
        result: User = await service.login_user(login_data)

        # Create access token
        access_token = create_access_token(data={"sub": result.username})

        # Set cookie
        set_auth_cookie(response, access_token)

        return BaseResponse(
            success=True, data=result, message="User logged in successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}",
        )


@router.post("/logout", tags=["User"])
async def logout_user(response: Response):
    """
    Log out the current user.

    Clears the authentication cookie.

    Args:
        response: FastAPI response object for clearing cookies

    Returns:
        BaseResponse indicating successful logout
    """
    clear_auth_cookie(response)
    return BaseResponse(success=True, message="User logged out successfully")


@router.post(
    path="/reset-password", response_model=BaseResponse[UserPublicModel], tags=["User"]
)
async def reset_password(
    reset_data: UserPasswordResetModel, session: SessionDep, new_password: str
) -> BaseResponse[User]:
    """
    Reset a user's password.

    Resets the password for a user with the provided email.

    Args:
        reset_data: The password reset data
        session: Database session dependency
        new_password: The new password

    Returns:
        BaseResponse containing the user with updated password

    Raises:
        HTTPException: 400 - Invalid input data
        HTTPException: 404 - User not found
        HTTPException: 500 - Internal server error
    """
    try:
        service: UserApplicationService = UserApplicationService(session)
        result: User = await service.reset_password(reset_data, new_password)
        return BaseResponse(
            success=True, data=result, message="Password reset successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}",
        )


@router.get(path="/me", response_model=BaseResponse[UserPublicModel], tags=["User"])
async def get_current_user_info(
    request: Request, session: SessionDep
) -> BaseResponse[User]:
    """
    Get the current authenticated user's information.

    Retrieves information about the currently logged-in user.

    Args:
        request: FastAPI request object for accessing cookies
        session: Database session dependency

    Returns:
        BaseResponse containing the current user's information

    Raises:
        HTTPException: 401 - Not authenticated
        HTTPException: 404 - User not found
        HTTPException: 500 - Internal server error
    """
    try:
        user = await get_current_user_from_cookie(request, session)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
            )
        return BaseResponse(
            success=True, data=user, message="Current user retrieved successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}",
        )


@router.get(
    path="/{user_id}", response_model=BaseResponse[UserPublicModel], tags=["User"]
)
async def read_user(
    user_id: uuid.UUID, session: SessionDep, current_user: User = Depends(get_current_user)
) -> BaseResponse[User]:
    """
    Get a user by ID.

    Retrieves a specific user by its unique identifier.

    Args:
        user_id: The ID of the user to retrieve
        session: Database session dependency
        current_user: Currently authenticated user

    Returns:
        BaseResponse containing the requested user

    Raises:
        HTTPException: 403 - Insufficient permissions
        HTTPException: 404 - User not found
        HTTPException: 500 - Internal server error
    """
    # Check if user has permission to view this user
    if current_user.id != user_id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this user",
        )

    try:
        service: UserApplicationService = UserApplicationService(session)
        result: User = await service.get_user(user_id)
        return BaseResponse(
            success=True, data=result, message="User retrieved successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}",
        )


@router.put(
    path="/{user_id}", response_model=BaseResponse[UserPublicModel], tags=["User"]
)
async def update_user(
    user_id: int,
    session: SessionDep,
    current_user: User = Depends(get_current_user),
    user_data: Optional[UserUpdateModel] = None,
):
    """
    Update a user.

    Updates an existing user with the provided data.

    Args:
        user_id: The ID of the user to update
        session: Database session dependency
        current_user: Currently authenticated user
        user_data: The updated data for the user

    Returns:
        BaseResponse containing the updated user

    Raises:
        HTTPException: 400 - Invalid input data
        HTTPException: 403 - Insufficient permissions
        HTTPException: 404 - User not found
        HTTPException: 500 - Internal server error
    """
    try:
        service = UserApplicationService(session)
        result = await service.update_user(
            user_id, user_data or UserUpdateModel(), current_user
        )
        return BaseResponse(
            success=True, data=result, message="User updated successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}",
        )


@router.delete(
    path="/{user_id}", response_model=BaseResponse[UserPublicModel], tags=["User"]
)
async def delete_user(
    user_id: uuid.UUID,
    session: SessionDep,
    current_user: User = Depends(get_current_user),
) -> BaseResponse[User]:
    """
    Delete a user (soft delete).

    Marks a user as inactive (soft delete) rather than removing it from the database.

    Args:
        user_id: The ID of the user to delete
        session: Database session dependency
        current_user: Currently authenticated user

    Returns:
        BaseResponse containing the deleted user

    Raises:
        HTTPException: 403 - Insufficient permissions
        HTTPException: 404 - User not found
        HTTPException: 500 - Internal server error
    """
    try:
        service: UserApplicationService = UserApplicationService(session)
        result: User = await service.delete_user(user_id, current_user)
        return BaseResponse(
            success=True, data=result, message="User deleted successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}",
        )
