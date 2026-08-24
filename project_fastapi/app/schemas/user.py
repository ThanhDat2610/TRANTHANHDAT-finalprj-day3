from datetime import datetime

from pydantic import BaseModel, ConfigDict


# =========================
# Base
# =========================

class UserBase(BaseModel):
    email: str
    full_name: str
    role: str = "USER"


# =========================
# Create
# =========================

class UserCreate(UserBase):
    password: str


# =========================
# Update
# =========================

class UserUpdate(BaseModel):
    email: str | None = None
    full_name: str | None = None
    password: str | None = None
    role: str | None = None
    is_active: bool | None = None


# =========================
# Response
# =========================

class UserResponse(UserBase):
    id: str
    is_active: bool
    created_at: datetime
    
    model_config = ConfigDict(
        from_attributes=True
    )