import uuid
import hashlib
from apps.user.application.schema import UserBase
from sqlmodel import Field, SQLModel
from datetime import datetime, timezone
from typing import Optional



###################################
##### User Database Models ########
###################################


class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    username: str = Field(unique=True, index=True, max_length=50)
    email: str = Field(unique=True, index=True, max_length=100)
    password: str = Field(max_length=255)
    first_name: str = Field(max_length=50)
    last_name: str = Field(max_length=50)
    is_active: bool = Field(default=True)
    is_superuser: bool = Field(default=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    def set_password(self, password: str):
        """Hash and set the user's password"""
        self.password = hashlib.sha256(password.encode()).hexdigest()
    
    def check_password(self, password: str) -> bool:
        """Check if the provided password matches the hashed password"""
        return self.password == hashlib.sha256(password.encode()).hexdigest()