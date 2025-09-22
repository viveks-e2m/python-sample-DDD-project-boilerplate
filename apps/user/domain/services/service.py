import uuid
from datetime import datetime, timedelta, timezone
from sqlmodel import select
from apps.user.domain.models.models import User, PasswordResetToken
from apps.user.domain.models.auth_models import Role
from apps.user.application.schema.schema import (
    UserCreateModel,
    UserUpdateModel,
    UserLoginModel,
)
from apps.user.domain.exceptions import (
    UserNotFoundError,
    UserPermissionError,
    UserValidationError,
    UserAuthenticationError,
    UserAlreadyExistsError,
)
from database import Session
from typing import Optional
import secrets


class UserDomainService:
    """
    Domain layer service class for user operations
    """

    def __init__(self, session: Session):
        self.session = session

    async def create_user(self, user_data: UserCreateModel):
        """
        Domain layer service for creating a user

        Args:
            user_data (UserCreateModel): The data for the new user

        Returns:
            User: The created user

        Raises:
            UserAlreadyExistsError: If a user with the same username or email already exists
            UserValidationError: If the user data is invalid
        """
        # Check if user with same username or email already exists
        username_check = select(User).where(User.username == user_data.username)
        email_check = select(User).where(User.email == user_data.email)

        if self.session.exec(username_check).first():
            raise UserAlreadyExistsError(
                f"User with username '{user_data.username}' already exists"
            )

        if self.session.exec(email_check).first():
            raise UserAlreadyExistsError(
                f"User with email '{user_data.email}' already exists"
            )

        # Get the default "User" role
        role_statement = select(Role).where(Role.name == "User")
        user_role = self.session.exec(role_statement).first()
        
        # Create user instance with default role
        user = User(
            username=user_data.username,
            email=user_data.email,
            password="",  # Will be set by set_password
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            is_active=True,
            is_superuser=False,
            role_id=user_role.id if user_role else None,  # Assign default User role if it exists
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

        # Set password
        user.set_password(user_data.password)

        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)

        return user

    async def get_user(self, user_id: uuid.UUID):
        """
        Domain layer service for retrieving a user

        Args:
            user_id (uuid.UUID): The ID of the user to retrieve

        Returns:
            User: The requested user

        Raises:
            UserNotFoundError: If the user is not found
        """
        statement = select(User).where(User.id == user_id, User.is_active == True)
        user = self.session.exec(statement).first()
        if not user:
            raise UserNotFoundError("User not found")
        return user

    async def get_user_by_username(self, username: str):
        """
        Domain layer service for retrieving a user by username

        Args:
            username (str): The username of the user to retrieve

        Returns:
            User: The requested user

        Raises:
            UserNotFoundError: If the user is not found
        """
        statement = select(User).where(
            User.username == username, User.is_active == True
        )
        user = self.session.exec(statement).first()
        if not user:
            raise UserNotFoundError("User not found")
        return user

    async def update_user(self, user_id: uuid.UUID, user_data: UserUpdateModel):
        """
        Domain layer service for updating a user

        Args:
            user_id (uuid.UUID): The ID of the user to update
            user_data (UserUpdateModel): The updated data for the user

        Returns:
            User: The updated user

        Raises:
            UserNotFoundError: If the user is not found
        """
        statement = select(User).where(User.id == user_id, User.is_active == True)
        user = self.session.exec(statement).first()

        if not user:
            raise UserNotFoundError("User not found")

        if user_data.first_name is not None:
            user.first_name = user_data.first_name

        if user_data.last_name is not None:
            user.last_name = user_data.last_name

        user.updated_at = datetime.now(timezone.utc)

        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)

        return user

    async def delete_user(self, user_id: uuid.UUID):
        """
        Domain layer service for deleting a user (soft delete)

        Args:
            user_id (uuid.UUID): The ID of the user to delete

        Returns:
            User: The deleted user

        Raises:
            UserNotFoundError: If the user is not found
        """
        statement = select(User).where(User.id == user_id)
        user = self.session.exec(statement).first()

        if not user:
            raise UserNotFoundError("User not found")

        user.is_active = False
        user.updated_at = datetime.now(timezone.utc)

        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)

        return user

    async def authenticate_user(self, login_data: UserLoginModel):
        """
        Domain layer service for authenticating a user

        Args:
            login_data (UserLoginModel): The login credentials

        Returns:
            User: The authenticated user

        Raises:
            UserNotFoundError: If the user is not found
            UserAuthenticationError: If the password is incorrect
        """
        statement = select(User).where(
            User.email == login_data.email, User.is_active == True
        )
        user = self.session.exec(statement).first()

        if not user:
            raise UserNotFoundError("User not found")

        if not user.check_password(login_data.password):
            raise UserAuthenticationError("Incorrect password")

        return user

    async def reset_password(self, email: str, new_password: str):
        """
        Domain layer service for resetting a user's password

        Args:
            email (str): The email of the user
            new_password (str): The new password

        Returns:
            User: The user with the updated password

        Raises:
            UserNotFoundError: If the user is not found
        """
        statement = select(User).where(User.email == email, User.is_active == True)
        user = self.session.exec(statement).first()

        if not user:
            raise UserNotFoundError("User not found")

        user.set_password(new_password)
        user.updated_at = datetime.now(timezone.utc)

        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)

        return user

    async def create_password_reset_token(self, email: str) -> PasswordResetToken:
        """
        Domain layer service for creating a password reset token

        Args:
            email (str): The email of the user requesting password reset

        Returns:
            PasswordResetToken: The created password reset token

        Raises:
            UserNotFoundError: If the user is not found
        """
        # Find the user by email
        statement = select(User).where(User.email == email, User.is_active == True)
        user = self.session.exec(statement).first()

        if not user:
            raise UserNotFoundError("User not found")

        # Invalidate any existing tokens for this user
        existing_tokens_statement = select(PasswordResetToken).where(
            PasswordResetToken.user_id == user.id, PasswordResetToken.used == False
        )
        existing_tokens = self.session.exec(existing_tokens_statement).all()
        for token in existing_tokens:
            token.used = True
            self.session.add(token)

        # Create a new reset token
        token_value = secrets.token_urlsafe(32)
        expires_at = datetime.now(timezone.utc) + timedelta(
            minutes=30
        )  # 30-minute expiration

        reset_token = PasswordResetToken(
            user_id=user.id,
            token=token_value,
            expires_at=expires_at,
            used=False,
            created_at=datetime.now(timezone.utc),
        )

        self.session.add(reset_token)
        self.session.commit()
        self.session.refresh(reset_token)

        return reset_token

    async def validate_password_reset_token(self, token: str) -> PasswordResetToken:
        """
        Domain layer service for validating a password reset token

        Args:
            token (str): The token to validate

        Returns:
            PasswordResetToken: The validated password reset token

        Raises:
            UserNotFoundError: If the token is invalid, expired, or already used
        """
        statement = select(PasswordResetToken).where(PasswordResetToken.token == token)
        reset_token = self.session.exec(statement).first()

        if not reset_token:
            raise UserNotFoundError("Invalid reset token")

        if reset_token.used:
            raise UserNotFoundError("Reset token has already been used")

        # Ensure both datetimes are timezone-aware for comparison
        expires_at = reset_token.expires_at
        if expires_at.tzinfo is None:
            # If expires_at is naive, assume it's UTC
            expires_at = expires_at.replace(tzinfo=timezone.utc)

        now = datetime.now(timezone.utc)

        if expires_at < now:
            raise UserNotFoundError("Reset token has expired")

        return reset_token

    async def complete_password_reset(self, token: str, new_password: str) -> User:
        """
        Domain layer service for completing a password reset

        Args:
            token (str): The reset token
            new_password (str): The new password

        Returns:
            User: The user with the updated password

        Raises:
            UserNotFoundError: If the token is invalid, expired, or already used
        """
        # Validate the token
        reset_token = await self.validate_password_reset_token(token)

        # Get the user
        statement = select(User).where(
            User.id == reset_token.user_id, User.is_active == True
        )
        user = self.session.exec(statement).first()

        if not user:
            raise UserNotFoundError("User not found")

        # Update the user's password
        user.set_password(new_password)
        user.updated_at = datetime.now(timezone.utc)

        # Mark the token as used
        reset_token.used = True

        # Save changes
        self.session.add(user)
        self.session.add(reset_token)
        self.session.commit()
        self.session.refresh(user)
        self.session.refresh(reset_token)

        return user

    async def list_users(self, skip: int, limit: int, active_only: bool):
        """
        Domain layer service for listing users with pagination and filtering

        Args:
            skip (int): Number of users to skip (for pagination)
            limit (int): Maximum number of users to return (for pagination)
            active_only (bool): Filter to show only active users

        Returns:
            List[User]: List of users
        """
        statement = select(User)

        if active_only:
            statement = statement.where(User.is_active == True)

        statement = statement.offset(skip).limit(limit)

        users = self.session.exec(statement).all()
        return users

    async def admin_update_user(self, user_id: uuid.UUID, user_data: UserUpdateModel):
        """
        Domain layer service for admin updating a user

        Args:
            user_id (uuid.UUID): The ID of the user to update
            user_data (UserUpdateModel): The updated data for the user

        Returns:
            User: The updated user

        Raises:
            UserNotFoundError: If the user is not found
        """
        statement = select(User).where(User.id == user_id)
        user = self.session.exec(statement).first()

        if not user:
            raise UserNotFoundError("User not found")

        if user_data.first_name is not None:
            user.first_name = user_data.first_name

        if user_data.last_name is not None:
            user.last_name = user_data.last_name

        user.updated_at = datetime.now(timezone.utc)

        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)

        return user

    async def update_user_status(
        self, user_id: uuid.UUID, is_active: bool, is_superuser: Optional[bool] = None
    ):
        """
        Domain layer service for updating a user's status

        Args:
            user_id (uuid.UUID): The ID of the user to update
            is_active (bool): Whether the user should be active
            is_superuser (Optional[bool]): Whether the user should be a superuser

        Returns:
            User: The updated user

        Raises:
            UserNotFoundError: If the user is not found
        """
        statement = select(User).where(User.id == user_id)
        user = self.session.exec(statement).first()

        if not user:
            raise UserNotFoundError("User not found")

        user.is_active = is_active

        if is_superuser is not None:
            user.is_superuser = is_superuser

        user.updated_at = datetime.now(timezone.utc)

        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)

        return user

    async def list_users_by_role(self, current_user: User):
        """
        Domain layer service for listing users based on the current user's permissions
        - Users with 'list_all_users_admin' permission: Can see all users
        - Users with 'list_all_users_role_maintainer' permission: Can see users with roles 'Maintainer' and 'User'
        - Users with 'list_all_users_role_user' permission: Can see only users with role 'User'

        Args:
            current_user (User): The authenticated user making the request

        Returns:
            List[User]: List of users based on permissions
        """
        from apps.user.domain.services.role_service import RoleService
        role_service = RoleService(self.session)
        
        # Superusers can see all users
        if current_user.is_superuser:
            statement = select(User)
            users = self.session.exec(statement).all()
            return users

        # Build query based on permissions
        statement = select(User)
        
        # Check for admin permission first
        if role_service.user_has_permission(current_user, "list_all_users_admin"):
            # Admin can see all users
            users = self.session.exec(statement).all()
            return users
        elif role_service.user_has_permission(current_user, "list_all_users_role_maintainer"):
            # Maintainer can see users with roles 'Maintainer' and 'User'
            role_statement = select(Role).where(
                (Role.name == "Maintainer") | (Role.name == "User")
            )
            allowed_roles = self.session.exec(role_statement).all()
            allowed_role_ids = [role.id for role in allowed_roles]
            
            # Include users with no role as well (they default to User role)
            from sqlmodel import col
            statement = statement.where(
                (col(User.role_id).in_(allowed_role_ids)) | (col(User.role_id).is_(None))
            )
            users = self.session.exec(statement).all()
            return users
        elif role_service.user_has_permission(current_user, "list_all_users_role_user"):
            # Regular users can only see users with role 'User' or no role
            role_statement = select(Role).where(Role.name == "User")
            user_role = self.session.exec(role_statement).first()
            
            from sqlmodel import col
            if user_role:
                statement = statement.where(
                    (col(User.role_id) == user_role.id) | (col(User.role_id).is_(None))
                )
            else:
                # If 'User' role doesn't exist, only show users with no role
                statement = statement.where(col(User.role_id).is_(None))
                
            users = self.session.exec(statement).all()
            return users
        else:
            # User has no relevant permissions, can only see themselves
            return [current_user]
