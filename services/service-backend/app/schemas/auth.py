from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict, field_serializer
from typing import Optional, Union, Any
from datetime import datetime
from uuid import UUID


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class SetupAdminRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class SetPasswordRequest(BaseModel):
    token: str
    password: str = Field(min_length=8)


class ResetPasswordRequest(BaseModel):
    email: EmailStr


class UserResponse(BaseModel):
    id: str
    email: str
    first_name: Optional[str]
    last_name: Optional[str]
    role: str
    is_guest: bool
    is_active: bool
    created_at: datetime
