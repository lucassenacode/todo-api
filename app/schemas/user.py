from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"


class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=72)


class UserRead(UserBase):
    id: int
    name: Optional[str] = None
    role: UserRole

    model_config = ConfigDict(from_attributes=True)


class UserProfileUpdate(BaseModel):
    name: Optional[str] = None
    new_password: Optional[str] = Field(
        default=None,
        min_length=8,
        max_length=72,
    )


class UserList(BaseModel):
    items: List[UserRead]
    total: int
