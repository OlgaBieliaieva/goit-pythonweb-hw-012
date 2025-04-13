from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict, EmailStr

from src.conf import constants
from src.models.user_model import UserRole


class UserBase(BaseModel):
    username: str = Field(min_length=constants.USERNAME_MIN_LENGTH, max_length=constants.USERNAME_MAX_LENGTH, description="Username")
    email: EmailStr

class UserCreate(UserBase):
    password: str = Field(min_length=constants.PASSWORD_MIN_LENGTH, max_length=constants.PASSWORD_MAX_LENGTH, description="Password")

class ResetPassword(BaseModel):
    token: str
    new_password: str = Field(min_length=constants.PASSWORD_MIN_LENGTH, max_length=constants.PASSWORD_MAX_LENGTH, description="Password")


class UserResponse(UserBase):
    id: int
    avatar: str | None
    role: UserRole
    

    model_config = ConfigDict(from_attributes=True)