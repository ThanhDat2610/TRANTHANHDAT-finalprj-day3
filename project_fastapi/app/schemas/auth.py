from typing import Optional
from pydantic import BaseModel

class UserRegisterRequest(BaseModel):
    username: str
    password: str
    email: str
    role: Optional[str] = "user"

class UserLoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str

class UserResponse(BaseModel):
    id: int
    username: str
    role: str

    class Config:
        from_attributes = True

