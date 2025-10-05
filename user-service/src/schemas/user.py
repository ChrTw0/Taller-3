"""User Service Pydantic Schemas."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict

# Base schemas
class UserBase(BaseModel):
    """Base user schema with common fields."""
    email: EmailStr
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    role: str = Field(default="student", pattern="^(student|teacher|admin)$")

# Request schemas
class UserCreate(UserBase):
    """Schema for creating a new user."""
    code: str = Field(..., min_length=3, max_length=20)
    password: str = Field(..., min_length=8, max_length=50)

class UserUpdate(BaseModel):
    """Schema for updating user profile."""
    email: Optional[EmailStr] = None
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    is_active: Optional[bool] = None

class UserLogin(BaseModel):
    """Schema for user login."""
    email: EmailStr
    password: str

class PasswordChange(BaseModel):
    """Schema for changing password."""
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=50)

# Response schemas
class UserResponse(UserBase):
    """Schema for user response."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime

class UserPublic(BaseModel):
    """Public user info (without sensitive data)."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    first_name: str
    last_name: str
    role: str
    is_active: bool

class UserInternal(BaseModel):
    """Internal user info (for inter-service communication)."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    email: EmailStr
    first_name: str
    last_name: str
    role: str
    is_active: bool
    is_verified: bool

# Auth schemas
class Token(BaseModel):
    """JWT Token response."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int

class TokenData(BaseModel):
    """Token payload data."""
    user_id: Optional[int] = None
    email: Optional[str] = None

# API Response schemas
class BaseResponse(BaseModel):
    """Base API response."""
    success: bool = True
    message: str = "Operation completed successfully"

class UserCreateResponse(BaseResponse):
    """User creation response."""
    data: UserResponse

class UserLoginResponse(BaseResponse):
    """User login response."""
    data: Token
    user: UserPublic

class ErrorResponse(BaseModel):
    """Error response schema."""
    success: bool = False
    message: str
    error_code: Optional[str] = None
    details: Optional[dict] = None