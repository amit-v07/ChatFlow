from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
import uuid
from typing import Optional


class UserCreate(BaseModel):
    """Schema for user registration."""
    email: EmailStr
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters")


class UserResponse(BaseModel):
    """Schema for user response (without password)."""
    id: uuid.UUID
    email: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserInDB(BaseModel):
    """Schema for user stored in database."""
    id: uuid.UUID
    email: str
    password_hash: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
