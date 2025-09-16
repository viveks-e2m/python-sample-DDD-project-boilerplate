from typing import Optional, Generic, TypeVar
from sqlmodel import SQLModel, Field
from pydantic import field_validator, BaseModel

T = TypeVar("T")

class BaseResponse(BaseModel, Generic[T]):
    success: bool
    message: str
    data: Optional[T] = None

class DemoBase(SQLModel):
    title: str = Field(max_length=100, min_length=1)
    description: str = Field(max_length=500, min_length=1)
    priority: int = Field(default=0, ge=0, le=10)

    @field_validator('title')
    def validate_title(cls, v):
        """
        Validate that title is not empty or whitespace only
        
        Args:
            v (str): The title to validate
            
        Returns:
            str: The validated title
            
        Raises:
            ValueError: If title is empty or whitespace only
        """
        if not v or not v.strip():
            raise ValueError('Title cannot be empty or whitespace only')
        return v.strip()

    @field_validator('description')
    def validate_description(cls, v):
        """
        Validate that description is not empty or whitespace only
        
        Args:
            v (str): The description to validate
            
        Returns:
            str: The validated description
            
        Raises:
            ValueError: If description is empty or whitespace only
        """
        if not v or not v.strip():
            raise ValueError('Description cannot be empty or whitespace only')
        return v.strip()

    @field_validator('priority')
    def validate_priority(cls, v):
        """
        Validate that priority is within acceptable range
        
        Args:
            v (int): The priority to validate
            
        Returns:
            int: The validated priority
            
        Raises:
            ValueError: If priority is not within acceptable range
        """
        if not 0 <= v <= 10:
            raise ValueError('Priority must be between 0 and 10')
        return v


class DemoPublicModel(SQLModel):
    id: int
    title: str
    description: str
    priority: int
    created_by: str
    created_at: str
    modified_at: str


class DemoCreateModel(DemoBase):
    pass


class DemoUpdateModel(SQLModel):
    title: Optional[str] = Field(default=None, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    priority: Optional[int] = Field(default=None, ge=0, le=10)

    @field_validator('title')
    def validate_title(cls, v):
        """
        Validate that title is not empty or whitespace only
        
        Args:
            v (str): The title to validate
            
        Returns:
            str: The validated title
            
        Raises:
            ValueError: If title is empty or whitespace only
        """
        if v is not None:
            if not v or not v.strip():
                raise ValueError('Title cannot be empty or whitespace only')
            return v.strip()
        return v

    @field_validator('description')
    def validate_description(cls, v):
        """
        Validate that description is not empty or whitespace only
        
        Args:
            v (str): The description to validate
            
        Returns:
            str: The validated description
            
        Raises:
            ValueError: If description is empty or whitespace only
        """
        if v is not None:
            if not v or not v.strip():
                raise ValueError('Description cannot be empty or whitespace only')
            return v.strip()
        return v

    @field_validator('priority')
    def validate_priority(cls, v):
        """
        Validate that priority is within acceptable range
        
        Args:
            v (int): The priority to validate
            
        Returns:
            int: The validated priority
            
        Raises:
            ValueError: If priority is not within acceptable range
        """
        if v is not None and not 0 <= v <= 10:
            raise ValueError('Priority must be between 0 and 10')
        return v