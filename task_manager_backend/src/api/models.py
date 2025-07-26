from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime

# PUBLIC_INTERFACE
class UserRegisterRequest(BaseModel):
    """Schema for registering a new user."""
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., min_length=6, description="Password for the user")

# PUBLIC_INTERFACE
class UserLoginRequest(BaseModel):
    """Schema for login request."""
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., min_length=6, description="Password for the user")

# PUBLIC_INTERFACE
class UserResponse(BaseModel):
    """Response schema for user information."""
    user_id: str
    email: EmailStr

# PUBLIC_INTERFACE
class AuthTokenResponse(BaseModel):
    """Response after login/register with session token."""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

# PUBLIC_INTERFACE
class TaskCreateRequest(BaseModel):
    """Schema for creating a task."""
    title: str = Field(..., description="Task title")
    description: Optional[str] = Field(None, description="Task details")
    status: Optional[str] = Field("pending", description="Task status")

# PUBLIC_INTERFACE
class TaskUpdateRequest(BaseModel):
    """Schema for updating a task."""
    title: Optional[str] = Field(None, description="Task title")
    description: Optional[str] = Field(None, description="Task details")
    status: Optional[str] = Field(None, description="Task status")

# PUBLIC_INTERFACE
class TaskResponse(BaseModel):
    """Schema for task details."""
    id: str
    user_id: str
    title: str
    description: Optional[str]
    status: str
    created_at: datetime
    updated_at: datetime

# PUBLIC_INTERFACE
class TaskListResponse(BaseModel):
    """Returned for task listing endpoints."""
    tasks: List[TaskResponse]
