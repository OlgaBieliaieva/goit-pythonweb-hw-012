from datetime import datetime, date
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict, EmailStr

from src.conf import constants
from src.conf import messages


class ContactSchema(BaseModel):
    first_name: str = Field(
        min_length=constants.NAME_MIN_LENGTH,
        max_length=constants.NAME_MAX_LENGTH,
        description=messages.contact_schema_first_name["ua"],
    )
    last_name: str = Field(
        min_length=constants.NAME_MIN_LENGTH,
        max_length=constants.NAME_MAX_LENGTH,
        description=messages.contact_schema_last_name["ua"],
    )
    email: EmailStr = Field(description=messages.contact_schema_email["ua"])
    phone: str = Field(
        min_length=constants.PHONE_MIN_LENGTH,
        max_length=constants.PHONE_MAX_LENGTH,
        description=messages.contact_schema_phone["ua"],
    )
    birth_date: Optional[date] = Field(
        default=None, description=messages.contact_schema_birth_date["ua"]
    )
    additionally: Optional[str] = Field(
        default=None,
        max_length=constants.ADDITIONALLY_MAX_LENGTH,
        description=messages.contact_schema_additionally["ua"],
    )


class ContactUpdateSchema(BaseModel):
    first_name: Optional[str] = Field(
        default=None,
        min_length=constants.NAME_MIN_LENGTH,
        max_length=constants.NAME_MAX_LENGTH,
        description=messages.contact_schema_first_name["ua"],
    )
    last_name: Optional[str] = Field(
        default=None,
        min_length=constants.NAME_MIN_LENGTH,
        max_length=constants.NAME_MAX_LENGTH,
        description=messages.contact_schema_last_name["ua"],
    )
    email: Optional[EmailStr] = Field(None, description=messages.contact_schema_email["ua"])
    phone: Optional[str] = Field(
        default=None,
        min_length=constants.PHONE_MIN_LENGTH,
        max_length=constants.PHONE_MAX_LENGTH,
        description=messages.contact_schema_phone["ua"],
    )
    birth_date: Optional[date] = Field(
        default=None, description=messages.contact_schema_birth_date["ua"]
    )
    additionally: Optional[str] = Field(
        default=None,
        max_length=constants.ADDITIONALLY_MAX_LENGTH,
        description=messages.contact_schema_additionally["ua"],
    )

class ContactResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    birth_date: Optional[date]
    additionally: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)