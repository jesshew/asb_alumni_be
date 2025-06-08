from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    """Base model for user data."""
    user_email: EmailStr
    user_name: Optional[str] = Field(None, max_length=255)
    user_google_id: Optional[str] = Field(None, max_length=255)
    user_linkedin_url: Optional[str] = Field(None, max_length=255)
    user_alumni_id: Optional[int] = None
    user_is_admin: Optional[bool] = False

class UserCreate(UserBase):
    """Model for creating new user records."""
    pass

class UserUpdate(BaseModel):
    """Model for updating user records."""
    user_email: Optional[EmailStr] = None
    user_name: Optional[str] = Field(None, max_length=255)
    user_google_id: Optional[str] = Field(None, max_length=255)
    user_linkedin_url: Optional[str] = Field(None, max_length=255)
    user_alumni_id: Optional[int] = None
    user_is_admin: Optional[bool] = None

class UserResponse(UserBase):
    """Model for user response data."""
    user_id: int
    user_created_at: datetime

    class Config:
        from_attributes = True

class UserListResponse(BaseModel):
    """Model for paginated user list response."""
    users: list[UserResponse]
    total_count: int
    page: int
    page_size: int
    total_pages: int 