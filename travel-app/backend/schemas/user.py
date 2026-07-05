"""用户相关 Schema"""
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=64)


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=64)
    nickname: str = Field(min_length=1, max_length=20)


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserProfile"


class UserProfile(BaseModel):
    id: str
    email: str
    nickname: str
    avatar: str | None = None
    created_at: datetime | None = None


class GuestSession(BaseModel):
    """游客会话（未登录时的临时身份）"""
    guest_id: str
    expires_at: datetime


AuthResponse.model_rebuild()
