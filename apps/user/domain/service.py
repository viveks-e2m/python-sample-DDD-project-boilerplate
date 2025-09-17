from datetime import datetime, timezone
from sqlmodel import select
from apps.user.domain.models import User
from apps.user.application.schema import UserCreateModel, UserUpdateModel, UserLoginModel
from apps.user.domain.exceptions import (
    UserNotFoundError, 
    UserPermissionError, 
    UserValidationError,
    UserAuthenticationError,
    UserAlreadyExistsError
)
from database import Session
import hashlib


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
            raise UserAlreadyExistsError(f"User with username '{user_data.username}' already exists")
        
        if self.session.exec(email_check).first():
            raise UserAlreadyExistsError(f"User with email '{user_data.email}' already exists")
        
        # Create user
        user = User(
            username=user_data.username,
            email=user_data.email,
            password="",  # Will be set by set_password
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            is_active=True,
            is_superuser=False,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
        # Set password
        user.set_password(user_data.password)
        
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        
        return user
    
    async def get_user(self, user_id: int):
        """
        Domain layer service for retrieving a user
        
        Args:
            user_id (int): The ID of the user to retrieve
            
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
        statement = select(User).where(User.username == username, User.is_active == True)
        user = self.session.exec(statement).first()
        if not user:
            raise UserNotFoundError("User not found")
        return user
    
    async def update_user(self, user_id: int, user_data: UserUpdateModel):
        """
        Domain layer service for updating a user
        
        Args:
            user_id (int): The ID of the user to update
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
            
        # Update only provided fields
        if user_data.email is not None:
            # Check if email is already taken by another user
            email_check = select(User).where(User.email == user_data.email, User.id != user_id)
            if self.session.exec(email_check).first():
                raise UserValidationError("Email is already taken by another user")
            user.email = user_data.email
            
        if user_data.first_name is not None:
            user.first_name = user_data.first_name
            
        if user_data.last_name is not None:
            user.last_name = user_data.last_name
            
        user.updated_at = datetime.now(timezone.utc)
        
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        
        return user
    
    async def delete_user(self, user_id: int):
        """
        Domain layer service for deleting a user (soft delete)
        
        Args:
            user_id (int): The ID of the user to delete
            
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
        statement = select(User).where(User.username == login_data.username, User.is_active == True)
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