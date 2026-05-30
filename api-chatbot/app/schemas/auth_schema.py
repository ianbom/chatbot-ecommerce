from pydantic import BaseModel, EmailStr, Field

from app.model.enums import UserRole


class UserPublic(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: UserRole
    is_active: bool

    model_config = {"from_attributes": True}


class RegisterRequest(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserPublic


