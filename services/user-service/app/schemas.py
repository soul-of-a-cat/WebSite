from datetime import datetime, date
from typing import Optional, Any
from enum import Enum

from pydantic import BaseModel, EmailStr, field_validator, ConfigDict, Field
from pydantic.functional_validators import AfterValidator
from typing_extensions import Annotated

from models import UserManager, Profile


def normalize_email_validator(v: str) -> str:
    return UserManager.normalize_email(v)


def normalize_username_validator(v: str) -> str:
    return UserManager.normalize_username(v)


NormalizedEmail = Annotated[str, AfterValidator(normalize_email_validator)]
NormalizedUsername = Annotated[str, AfterValidator(normalize_username_validator)]


class ImageSize(str, Enum):
    ORIGINAL = "original"
    SIZE_300x300 = "300x300"
    SIZE_50x50 = "50x50"


class ProfileBase(BaseModel):
    birthday: Optional[date] = Field(
        None,
        description="Дата рождения пользователя"
    )
    image: Optional[str] = Field(
        None,
        description="Путь к изображению"
    )

    model_config = ConfigDict(from_attributes=True)


class ProfileCreate(ProfileBase):
    pass


class ProfileUpdate(ProfileBase):
    birthday: Optional[date] = None
    image: Optional[str] = None


class ProfileResponse(ProfileBase):
    id: int
    user_id: int
    attempts_count: int = 0
    block_date: Optional[datetime] = None
    image_url: Optional[str] = None
    image_300x300: Optional[str] = None
    image_50x50: Optional[str] = None

    @classmethod
    async def from_profile(cls, profile: Profile) -> 'ProfileResponse':
        return cls(
            id=profile.id,
            user_id=profile.user_id,
            birthday=profile.birthday,
            attempts_count=profile.attempts_count,
            block_date=profile.block_date,
            image=profile.image,
            image_url=await profile.get_image_url(),
            image_300x300=await profile.get_image_url("300x300"),
            image_50x50=await profile.get_image_url("50x50")
        )


class UserBase(BaseModel):
    username: NormalizedUsername = Field(
        ...,
        min_length=3,
        max_length=150,
        pattern=r'^[a-zA-Z0-9_.-]+$',
        description="Имя пользователя"
    )
    email: NormalizedEmail = Field(
        ...,
        description="Email пользователя"
    )
    first_name: str = Field(
        "",
        max_length=150,
        description="Имя пользователя"
    )
    last_name: str = Field(
        "",
        max_length=150,
        description="Фамилия пользователя"
    )

    @field_validator('email')
    @classmethod
    def validate_email_format(cls, v: str) -> str:
        import re
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, v):
            raise ValueError('Некорректный формат email')
        return v

    model_config = ConfigDict(from_attributes=True)


class UserCreate(UserBase):
    password: str = Field(
        ...,
        min_length=8,
        description="Пароль пользователя"
    )
    profile: Optional[ProfileCreate] = None

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Пароль должен содержать минимум 8 символов")
        if not any(char.isdigit() for char in v):
            raise ValueError("Пароль должен содержать хотя бы одну цифру")
        if not any(char.isalpha() for char in v):
            raise ValueError("Пароль должен содержать хотя бы одну букву")
        return v


class UserUpdate(BaseModel):
    username: Optional[NormalizedUsername] = None
    email: Optional[NormalizedEmail] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: Optional[bool] = None
    is_staff: Optional[bool] = None
    is_superuser: Optional[bool] = None
    profile: Optional[ProfileUpdate] = None


class UserLogin(BaseModel):
    email: NormalizedEmail = Field(..., description="Email пользователя")
    password: str = Field(..., description="Пароль пользователя")


class UserResponse(UserBase):
    id: int
    is_superuser: bool = False
    is_staff: bool = False
    is_active: bool = True
    date_joined: datetime
    last_login: Optional[datetime] = None
    profile: Optional[ProfileResponse] = None

    @classmethod
    async def from_user(cls, user: Any) -> 'UserResponse':
        profile_response = None
        if user.profile:
            profile_response = await ProfileResponse.from_profile(user.profile)

        return cls(
            id=user.id,
            username=user.username,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            is_superuser=user.is_superuser,
            is_staff=user.is_staff,
            is_active=user.is_active,
            date_joined=user.date_joined,
            last_login=user.last_login,
            profile=profile_response
        )


class UserWithTokenResponse(UserResponse):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: int
    username: str
    email: str
    is_superuser: bool = False
    exp: Optional[datetime] = None


UserResponse.model_rebuild()
ProfileResponse.model_rebuild()