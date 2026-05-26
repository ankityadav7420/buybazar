import re
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


EMAIL_PATTERN = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")
MOBILE_PATTERN = re.compile(r"^\+?[1-9]\d{9,14}$")


class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"


class UserCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: str = Field(max_length=255)
    age: int = Field(ge=13, le=120)
    mobile: str = Field(min_length=10, max_length=16)

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        email = value.strip().lower()

        if not EMAIL_PATTERN.match(email):
            raise ValueError("Enter a valid email address")

        return email

    @field_validator("mobile")
    @classmethod
    def validate_mobile(cls, value: str) -> str:
        mobile = value.strip().replace(" ", "").replace("-", "")

        if not MOBILE_PATTERN.match(mobile):
            raise ValueError("Mobile must be 10 to 15 digits and may start with +")

        return mobile


class UserResponse(BaseModel):
    id: UUID
    name: str
    email: str
    age: int
    mobile: str
    role: UserRole
    is_deleted: int

    class Config:
        from_attributes = True


class UserDataResponse(BaseModel):
    message: str
    data: UserResponse


class UsersListResponse(BaseModel):
    message: str
    data: list[UserResponse]
