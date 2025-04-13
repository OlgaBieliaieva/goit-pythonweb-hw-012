from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.contacts_repo import ContactRepository
from src.schemas.contact import ContactSchema, ContactUpdateSchema


class ContactService:
    def __init__(self, db: AsyncSession):
        self.contact_repository = ContactRepository(db)

    async def create_contact(self, body: ContactSchema, user):
        return await self.contact_repository.create_contact(body, user)

    async def get_contacts(self, user, first_name: Optional[str], 
        last_name: Optional[str], 
        email: Optional[str], 
        limit: int, 
        offset: int):
        return await self.contact_repository.get_contacts(
            user,
            first_name=first_name, 
            last_name=last_name, 
            email=email, 
            limit=limit, 
            offset=offset
        )

    async def get_contacts_by_upcoming_birthdays(
        self, 
        user,
        limit: int = 10, 
        offset: int = 0
    ):
        return await self.contact_repository.get_contacts_by_upcoming_birthdays(
            user,
            limit=limit, 
            offset=offset
        )

    async def get_contact(self, contact_id: int, user):
        return await self.contact_repository.get_contact_by_id(contact_id, user)

    async def update_contact(self, contact_id: int, body: ContactUpdateSchema, user):
        return await self.contact_repository.update_contact(contact_id, body, user)    

    async def remove_contact(self, contact_id: int, user):
        return await self.contact_repository.remove_contact(contact_id, user)