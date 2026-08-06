from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import Optional
from datetime import datetime
from core.config import settings
from utils.password import password_hasher

class UserResponse(BaseModel):
    id: int
    username: str
    last_login: Optional[datetime] = None
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: bool
    is_superuser: bool
    date_joined: datetime
    profile: Optional['ProfileResponse'] = None

    model_config = {"from_attributes": True}

class UserCreate(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=settings.PASSWORD_MIN_LENGTH)
    password_confirm: str

    @field_validator('username')
    @classmethod
    def validate_username(cls, value: str) -> str:
        if not value.isalnum() and "_" not in value:
            raise ValueError("Имя пользователя должно содержать только буквы, цифры и символы подчеркивания.")
        return value.lower()

    @field_validator('password_confirm')
    @classmethod
    def password_match(cls, value: str, info) -> str:
        if 'password' in info.data and value != info.data['password']:
            raise ValueError('Пароли не совпадают')
        return value

    @field_validator('password')
    @classmethod
    def validate_password_strength(cls, value: str) -> str:
        is_valid, error_msg = password_hasher.validate_strength(value)
        if not is_valid:
            raise ValueError(error_msg)
        return value

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserPasswordChange(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=settings.PASSWORD_MIN_LENGTH)
    new_password_confirm: str

    @field_validator('new_password_confirm')
    @classmethod
    def password_match(cls, value: str, info) -> str:
        if 'new_password' in info.data and value != info.data['new_password']:
            raise ValueError('Пароли не совпадают')
        return value

    @field_validator('new_password')
    @classmethod
    def validate_password_strength(cls, value: str) -> str:
        is_valid, error_msg = password_hasher.validate_strength(value)
        if not is_valid:
            raise ValueError(error_msg)
        return value

class UserPasswordReset(BaseModel):
    token: str
    new_password: str = Field(..., min_length=settings.PASSWORD_MIN_LENGTH)
    new_password_confirm: str

    @field_validator('new_password_confirm')
    @classmethod
    def password_match(cls, value: str, info) -> str:
        if 'new_password' in info.data and value != info.data['new_password']:
            raise ValueError('Пароли не совпадают')
        return value

class UserUpdate(BaseModel):
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: str = Field(..., min_length=3, max_length=50)

class ProfileResponse(BaseModel):
    id: int
    birthday: Optional[datetime] = None
    attempts_count: int
    block_date: Optional[datetime] = None
    user_id: int

class ProfileUpdate(BaseModel):
    birthday: Optional[datetime] = None