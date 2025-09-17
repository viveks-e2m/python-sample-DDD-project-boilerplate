import uuid
import hashlib
from typing import Optional, Generic, TypeVar
from sqlmodel import SQLModel, Field
from pydantic import field_validator, BaseModel, EmailStr
from datetime import datetime, timezone

T = TypeVar("T")

# -------------------------
# Generic API Response
# -------------------------
class BaseResponse(BaseModel, Generic[T]):
    success: bool
    message: str
    data: Optional[T] = None


# -------------------------
# Mixins for validation
# -------------------------
class UsernameValidatorMixin:
    @field_validator("username")
    def validate_username(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Username cannot be empty or whitespace only")
        if not v.replace("_", "").isalnum():
            raise ValueError("Username can only contain alphanumeric characters and underscores")
        return v.strip().lower()


class NameValidatorMixin:
    @field_validator("first_name", "last_name")
    def validate_name(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Name cannot be empty or whitespace only")
        return v.strip().title()


class PasswordValidatorMixin:
    @field_validator("password")
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v


# -------------------------
# Base Models
# -------------------------
class UserBase(SQLModel, UsernameValidatorMixin, NameValidatorMixin):
    username: str = Field(max_length=50, min_length=3)
    email: EmailStr = Field(max_length=100)
    first_name: str = Field(max_length=50)
    last_name: str = Field(max_length=50)


class UserCreateModel(UserBase, PasswordValidatorMixin):
    password: str = Field(min_length=8)


class UserUpdateModel(SQLModel, NameValidatorMixin):
    email: Optional[EmailStr] = Field(default=None, max_length=100)
    first_name: Optional[str] = Field(default=None, max_length=50)
    last_name: Optional[str] = Field(default=None, max_length=50)


class UserPublicModel(SQLModel):
    id: uuid.UUID
    username: str
    email: EmailStr
    first_name: str
    last_name: str
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime


class UserLoginModel(SQLModel):
    username: str = Field(min_length=3)
    password: str = Field(min_length=8)


class UserPasswordResetModel(SQLModel):
    email: EmailStr
