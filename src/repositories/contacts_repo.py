import logging
from typing import Sequence
from datetime import datetime, timedelta

from sqlalchemy import select, and_, extract
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.contact_model import Contact_model
from src.models.user_model import User
from src.schemas.contact import ContactSchema, ContactUpdateSchema

logger = logging.getLogger("uvicorn.error")


class ContactRepository:
    def __init__(self, session: AsyncSession):
        """
        Initialize the ContactRepository.

        Args:
            session: An AsyncSession object connected to the database.
        """
        self.db = session

    async def get_contacts(self, user: User, limit: int = 10, offset: int = 0,  first_name: str = None, last_name: str = None, email: str = None) -> Sequence[Contact_model]:
        """
        Retrieve a list of contacts for the given user with optional filters.

        Args:
            user: The User whose contacts are to be retrieved.
            limit: The maximum number of contacts to return (default is 10).
            offset: The number of contacts to skip (default is 0).
            first_name: Optional filter for contacts' first names.
            last_name: Optional filter for contacts' last names.
            email: Optional filter for contacts' emails.

        Returns:
            A list of Contact_model objects that match the filters.
        """
        filters = []
        
        if first_name:
            filters.append(Contact_model.first_name.ilike(f"%{first_name}%"))
        
        if last_name:
            filters.append(Contact_model.last_name.ilike(f"%{last_name}%"))
        
        if email:
            filters.append(Contact_model.email.ilike(f"%{email}%"))
        
        if user:
            filters.append(Contact_model.user_id == user.id)
        
        stmt = select(Contact_model).filter(and_(*filters)).offset(offset).limit(limit)
        contacts = await self.db.execute(stmt)
        return contacts.scalars().all()

    async def get_contacts_by_upcoming_birthdays(
        self, user: User, limit: int = 10, offset: int = 0
    ) -> list[Contact_model]:
        """
        Retrieve a list of contacts with upcoming birthdays within the next 7 days.

        Args:
            user: The User whose contacts' birthdays are being checked.
            limit: The maximum number of contacts to return (default is 10).
            offset: The number of contacts to skip (default is 0).

        Returns:
            A list of Contact_model objects with upcoming birthdays within 7 days.
        """
        today = datetime.now()
        current_month = today.month
        current_day = today.day   
        upcoming_birthday_end = today + timedelta(days=7)

        stmt = select(Contact_model).filter(           
            extract('month', Contact_model.birth_date) == current_month,
            extract('day', Contact_model.birth_date) >= current_day,
            extract('day', Contact_model.birth_date) <= upcoming_birthday_end.day,
            Contact_model.user_id == user.id
        ).order_by(Contact_model.birth_date).offset(offset).limit(limit)

        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_contact_by_id(self, contact_id: int, user: User) -> Contact_model | None:

        """
        Retrieve a contact by its ID for the given user.

        Args:
            contact_id: The ID of the contact to retrieve.
            user: The User who owns the contact.

        Returns:
            The Contact_model with the specified ID, or None if no such contact exists.
        """
        
        stmt = select(Contact_model).filter_by(id=contact_id, user_id=user.id)
        contact = await self.db.execute(stmt)
        return contact.scalar_one_or_none()

    async def create_contact(self, body: ContactSchema, user: User) -> Contact_model:
        """
        Create a new contact with the specified data.

        Args:
            body: A ContactSchema object containing the contact data.
            user: The User who owns the new contact.

        Returns:
            The newly created Contact_model.
        """
        contact = Contact_model(**body.model_dump(), user=user)
        self.db.add(contact)
        await self.db.commit()
        await self.db.refresh(contact)
        return contact

    async def remove_contact(self, contact_id: int, user: User) -> Contact_model | None:
        """
        Remove a contact by its ID for the given user.

        Args:
            contact_id: The ID of the contact to remove.
            user: The User who owns the contact.

        Returns:
            The removed Contact_model, or None if no contact with the given ID exists.
        """
        contact = await self.get_contact_by_id(contact_id, user)
        if contact:
            await self.db.delete(contact)
            await self.db.commit()
        return contact

    async def update_contact(
        self, contact_id: int, body: ContactUpdateSchema, user: User):
        """
        Update a contact's details.

        Args:
            contact_id: The ID of the contact to update.
            body: A ContactUpdateSchema object containing the updated data.
            user: The User who owns the contact.

        Returns:
            The updated Contact_model, or None if no contact with the given ID exists.
        """
        contact = await self.get_contact_by_id(contact_id, user)
        if contact:
            update_data = body.model_dump(exclude_unset=True)

            for key, value in update_data.items():
                setattr(contact, key, value)

            await self.db.commit()
            await self.db.refresh(contact)

        return contact