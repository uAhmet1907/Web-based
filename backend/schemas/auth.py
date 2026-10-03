from pydantic import BaseModel, EmailStr
from typing import Optional, List


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str


class RegisterRequest(BaseModel):
    full_name: str
    email: str
    phone: str
    password: str
    subjects: Optional[List[int]] = []


class RegisterResponse(BaseModel):
    id: int
    email: str
    is_approved: bool
    message: str


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str
