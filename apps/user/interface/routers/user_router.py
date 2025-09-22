import uuid
from fastapi.routing import APIRouter
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Path,
    Query,
    status,
    Response,
)
from apps.user.application.schema.schema import (
    UserCreateModel,
    UserPublicModel,
    UserUpdateModel,
    UserLoginModel,
    PasswordResetRequestModel,
    PasswordResetConfirmModel,
    BaseResponse,
)
from apps.user.application.services.service import UserApplicationService
from apps.user.utils import (
    set_auth_cookie,
    clear_auth_cookie,
    create_access_token,
)
from apps.user.domain.models.models import User
from database import SessionDep
from typing import List, Optional
from apps.user.interface.dependency import get_user_service, get_authenticated_user
from apps.user.interface import role_dependencies

router: APIRouter = APIRouter()


@router.post(
    path="/register", response_model=BaseResponse[UserPublicModel], tags=["User"]
)
async def register_user(
    user_data: UserCreateModel,
    service: UserApplicationService = Depends(get_user_service),
) -> BaseResponse[User]:
    """
    Register a new user.

    Creates a new user account with the provided data.

    Args:
        user_data: The data for the new user
        session: Database session dependency
        service: User application service (dependency injected)

    Returns:
        BaseResponse containing the created user

    Raises:
        HTTPException: 400 - Invalid input data
        HTTPException: 409 - User already exists
        HTTPException: 500 - Internal server error
    """
    try:
        result: User = await service.register_user(user_data)
        return BaseResponse(
            success=True,
            data=result,
            message="User registered successfully",
            status_code=status.HTTP_201_CREATED,
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}",
        )


@router.post(path="/login", response_model=BaseResponse[UserPublicModel], tags=["User"])
async def login_user(
    response: Response,
    login_data: UserLoginModel,
    service: UserApplicationService = Depends(get_user_service),
) -> BaseResponse[User]:
    """
    Authenticate a user.

    Authenticates a user with the provided credentials.

    Args:
        response: FastAPI response object for setting cookies
        login_data: The login credentials
        session: Database session dependency
        service: User application service (dependency injected)

    Returns:
        BaseResponse containing the authenticated user

    Raises:
        HTTPException: 400 - Invalid credentials
        HTTPException: 401 - Authentication failed
        HTTPException: 404 - User not found
        HTTPException: 500 - Internal server error
    """
    try:
        result: User = await service.login_user(login_data)

        # Create access token
        access_token = create_access_token(data={"sub": result.username})

        # Set cookie
        set_auth_cookie(response, access_token)

        return BaseResponse(
            success=True,
            data=result,
            message="User logged in successfully",
            status_code=status.HTTP_200_OK,
        )
    except HTTPException as e:
        raise e
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
    return BaseResponse(
        success=True,
        message="User logged out successfully",
        status_code=status.HTTP_200_OK,
    )


@router.post("/request-password-reset", tags=["User"])
async def request_password_reset(
    reset_data: PasswordResetRequestModel,
    service: UserApplicationService = Depends(get_user_service),
) -> BaseResponse[dict]:
    """
    Request a password reset.

    Sends a password reset link to the user's email.

    Args:
        reset_data: The password reset request data
        session: Database session dependency
        service: User application service (dependency injected)

    Returns:
        BaseResponse indicating successful request

    Raises:
        HTTPException: 500 - Internal server error
    """
    try:
        result = await service.request_password_reset(reset_data)
        return BaseResponse(
            success=True, data=result, message="Password reset request processed"
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}",
        )


@router.post("/confirm-password-reset", tags=["User"])
async def confirm_password_reset(
    reset_data: PasswordResetConfirmModel,
    service: UserApplicationService = Depends(get_user_service),
) -> BaseResponse[User]:
    """
    Confirm a password reset.

    Updates the user's password using the provided reset token.

    Args:
        reset_data: The password reset confirmation data
        session: Database session dependency
        service: User application service (dependency injected)

    Returns:
        BaseResponse containing the user with updated password

    Raises:
        HTTPException: 400 - Invalid token or password
        HTTPException: 500 - Internal server error
    """
    try:
        result: User = await service.confirm_password_reset(reset_data)
        return BaseResponse(
            success=True,
            data=result,
            message="Password reset successfully",
            status_code=status.HTTP_200_OK,
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}",
        )


@router.get(path="/me", response_model=BaseResponse[UserPublicModel], tags=["User"])
async def get_current_user_info(
    current_user: User = Depends(get_authenticated_user),
) -> BaseResponse[User]:
    """
    Get the current authenticated user's information.

    Retrieves information about the currently logged-in user.

    Args:
        current_user: The authenticated user (dependency injected)

    Returns:
        BaseResponse containing the current user's information

    Raises:
        HTTPException: 401 - Not authenticated
        HTTPException: 404 - User not found
        HTTPException: 500 - Internal server error
    """

    return BaseResponse(
        success=True,
        data=current_user,
        message="Current user retrieved successfully",
        status_code=status.HTTP_200_OK,
    )


@router.get(
    path="/", 
    response_model=BaseResponse[List[UserPublicModel]], 
    tags=["User"]
)
async def list_users_by_role(
    current_user: User = Depends(role_dependencies.require_user_listing_permission()),
    service: UserApplicationService = Depends(get_user_service),
) -> BaseResponse[List[User]]:
    """
    List users based on the current user's permissions.
    
    - Users with 'list_all_users_admin' permission: Can see all users
    - Users with 'list_all_users_role_maintainer' permission: Can see users with roles 'Maintainer' and 'User'
    - Users with 'list_all_users_role_user' permission: Can see only users with role 'User'

    Args:
        current_user: The authenticated user (dependency injected)
        service: User application service (dependency injected)

    Returns:
        BaseResponse containing list of users based on permissions

    Raises:
        HTTPException: 401 - Not authenticated
        HTTPException: 403 - Insufficient permissions
        HTTPException: 500 - Internal server error
    """
    try:
        users = await service.list_users_by_role(current_user)
        return BaseResponse(
            success=True,
            data=list(users),
            message="Users retrieved successfully",
            status_code=status.HTTP_200_OK,
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}",
        )
