from typing import Any, Optional
import uuid
from fastapi import Depends, HTTPException, status
from sqlmodel import select
from apps.user.domain.models import User
from apps.user.domain.service import UserDomainService
from apps.user.domain.exceptions import (
    UserNotFoundError, 
    UserPermissionError, 
    UserValidationError,
    UserAuthenticationError,
    UserAlreadyExistsError
)
from apps.user.application.schema import (
    UserCreateModel, 
    UserUpdateModel, 
    UserLoginModel,
    UserPasswordResetModel
)
from apps.user.utils import get_current_user
from database import SessionDep


class UserApplicationService:
    """
    Application layer service class for user operations
    """

    def __init__(self, session: SessionDep):
        self.session: SessionDep = session
        self.domain_service: UserDomainService = UserDomainService(session)

    async def register_user(self, user_data: UserCreateModel):
        """
        Application layer service for registering a new user

        Args:
            user_data (UserCreateModel): The data for the new user

        Returns:
            User: The created user

        Raises:
            HTTPException: 400 - Invalid input data
            HTTPException: 409 - User already exists
        """
        try:
            return await self.domain_service.create_user(user_data)
        except UserAlreadyExistsError as e:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=str(e)
            )
        except UserValidationError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create user: {str(e)}"
            )

    async def get_user(self, user_id: uuid.UUID):
        """
        Application layer service for retrieving a user

        Args:
            user_id (int): The ID of the user to retrieve

        Returns:
            User: The requested user

        Raises:
            HTTPException: 404 - User not found
        """
        try:
            return await self.domain_service.get_user(user_id)
        except UserNotFoundError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

    async def update_user(self, user_id: int, user_data: UserUpdateModel, current_user: User = Depends(get_current_user)):
        """
        Application layer service for updating a user

        Args:
            user_id (int): The ID of the user to update
            user_data (UserUpdateModel): The updated data for the user
            current_user (User): The currently authenticated user

        Returns:
            User: The updated user

        Raises:
            HTTPException: 400 - Invalid input data
            HTTPException: 403 - Insufficient permissions
            HTTPException: 404 - User not found
        """
        # Check if user has permission to update this user
        if current_user.id != user_id and not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this user"
            )
        
        try:
            return await self.domain_service.update_user(user_id, user_data)
        except UserNotFoundError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        except UserValidationError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )

    async def delete_user(self, user_id: uuid.UUID, current_user: User = Depends(get_current_user)):
        """
        Application layer service for deleting a user

        Args:
            user_id (uuid.UUID): The ID of the user to delete
            current_user (User): The currently authenticated user

        Returns:
            User: The deleted user

        Raises:
            HTTPException: 403 - Insufficient permissions
            HTTPException: 404 - User not found
        """
        # Check if user has permission to delete this user
        if current_user.id != user_id and not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this user"
            )
        
        try:
            return await self.domain_service.delete_user(user_id)
        except UserNotFoundError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

    async def login_user(self, login_data: UserLoginModel):
        """
        Application layer service for user login

        Args:
            login_data (UserLoginModel): The login credentials

        Returns:
            User: The authenticated user

        Raises:
            HTTPException: 400 - Invalid credentials
            HTTPException: 404 - User not found
        """
        try:
            return await self.domain_service.authenticate_user(login_data)
        except UserNotFoundError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        except UserAuthenticationError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password"
            )

    async def reset_password(self, reset_data: UserPasswordResetModel, new_password: str):
        """
        Application layer service for resetting a user's password

        Args:
            reset_data (UserPasswordResetModel): The password reset data
            new_password (str): The new password

        Returns:
            User: The user with the updated password

        Raises:
            HTTPException: 400 - Invalid input data
            HTTPException: 404 - User not found
        """

        try:
            return await self.domain_service.reset_password(reset_data.email, new_password)
        except UserNotFoundError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )