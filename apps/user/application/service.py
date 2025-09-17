from typing import Any, Optional
import uuid
from fastapi import Depends, HTTPException, status
from sqlmodel import select
from apps.user.domain.models import User, PasswordResetToken
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
    PasswordResetRequestModel,
    PasswordResetConfirmModel
)
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
            user_id (uuid.UUID): The ID of the user to retrieve

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

    async def update_user(self, user_id: uuid.UUID, user_data: UserUpdateModel):
        """
        Application layer service for updating a user

        Args:
            user_id (uuid.UUID): The ID of the user to update
            user_data (UserUpdateModel): The updated data for the user

        Returns:
            User: The updated user

        Raises:
            HTTPException: 400 - Invalid input data
            HTTPException: 404 - User not found
        """
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

    async def delete_user(self, user_id: uuid.UUID):
        """
        Application layer service for deleting a user

        Args:
            user_id (uuid.UUID): The ID of the user to delete

        Returns:
            User: The deleted user

        Raises:
            HTTPException: 404 - User not found
        """
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

    async def request_password_reset(self, reset_data: PasswordResetRequestModel):
        """
        Application layer service for requesting a password reset

        Args:
            reset_data (PasswordResetRequestModel): The password reset request data

        Returns:
            dict: Success message

        Raises:
            HTTPException: 404 - User not found
            HTTPException: 500 - Internal server error
        """
        try:
            reset_token = await self.domain_service.create_password_reset_token(reset_data.email)
            # In a real application, you would send an email with the reset link here
            # For now, we'll just return the token (in a real app, this should not be exposed)
            return {
                "message": "Password reset instructions sent to your email",
                "token": reset_token.token  # Remove this in production, only for testing
            }
        except UserNotFoundError:
            # We don't reveal whether the email exists for security reasons
            return {"message": "Password reset instructions sent to your email"}
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to process password reset request: {str(e)}"
            )

    async def confirm_password_reset(self, reset_data: PasswordResetConfirmModel):
        """
        Application layer service for confirming a password reset

        Args:
            reset_data (PasswordResetConfirmModel): The password reset confirmation data

        Returns:
            User: The user with the updated password

        Raises:
            HTTPException: 400 - Invalid token or password
            HTTPException: 404 - User not found
            HTTPException: 500 - Internal server error
        """
        try:
            user = await self.domain_service.complete_password_reset(
                reset_data.token, reset_data.new_password
            )
            return user
        except UserNotFoundError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to reset password: {str(e)}"
            )