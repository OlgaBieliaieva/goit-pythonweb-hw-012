import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.models.user_model import User
from src.utils.depend_service import get_current_user
from src.services.contacts import ContactService
from src.schemas.contact import (
    ContactResponse,
    ContactSchema,
    ContactUpdateSchema,
)


router = APIRouter(prefix="/contacts", tags=["contacts"])
logger = logging.getLogger("uvicorn.error")


@router.get("/", response_model=list[ContactResponse], name="Get all contacts",
    description="Get all contacts with filters",
    response_description="Contacts list",)
async def get_contacts(
    first_name: Optional[str] = Query(None),
    last_name: Optional[str] = Query(None),
    email: Optional[str] = Query(None),
    limit: int = Query(10, ge=10, le=500),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    contact_service = ContactService(db)
    return await contact_service.get_contacts(user, first_name=first_name, 
        last_name=last_name, 
        email=email, 
        limit=limit, 
        offset=offset)


@router.get("/birthdays", response_model=list[ContactResponse], name="Get contacts with upcoming birthdays", description="Get all contacts with upcoming birthdays by 7 days",
    response_description="Contacts list")
async def get_contacts_upcoming_birthdays(
    limit: int = Query(10, ge=10, le=500),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    contact_service = ContactService(db)
    return await contact_service.get_contacts_by_upcoming_birthdays(
        user,
        limit=limit, 
        offset=offset
    )

@router.get(
    "/{contact_id}",
    response_model=ContactResponse,
    name="Get contact by id",
    description="Get contact by id",
    response_description="Contact details",
)
async def get_contact(contact_id: int, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    contact_service = ContactService(db)
    contact = await contact_service.get_contact(contact_id, user)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact


@router.post(
    "/",
    response_model=ContactResponse,
    name="Create contact",
    description="Create new contact",
    response_description="Creating result",
    status_code=status.HTTP_201_CREATED,
)
async def create_contact(body: ContactSchema, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    contact_service = ContactService(db)
    return await contact_service.create_contact(body, user)


@router.put("/{contact_id}", response_model=ContactResponse,
    name="Update contact by id",
    description="Update contact fields",
    response_description="Updating result",)
async def update_contact(
    contact_id: int, body: ContactUpdateSchema, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)
):
    contact_service = ContactService(db)
    contact = await contact_service.update_contact(contact_id, body, user)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact


@router.delete("/{contact_id}", name="Remove contact by id",
    description="Remove contact", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact(contact_id: int, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    contact_service = ContactService(db)
    await contact_service.remove_contact(contact_id, user)
    return None