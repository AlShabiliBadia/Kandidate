from pydantic import BaseModel, EmailStr, field_validator, ConfigDict, field_serializer, Field
from typing import Optional, Union, Any
from datetime import datetime
from uuid import UUID


class CreateUserRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    role: str  # ADMIN, RECRUITER, or REVIEWER
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class InviteUserRequest(BaseModel):
    email: EmailStr
    role: str  # RECRUITER or REVIEWER
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class UpdateUserRequest(BaseModel):
    role: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: Optional[bool] = None


class UserListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    email: str
    first_name: Optional[str]
    last_name: Optional[str]
    role: str
    is_guest: bool
    is_active: bool
    created_at: datetime
