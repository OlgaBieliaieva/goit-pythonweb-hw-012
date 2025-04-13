import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession
from src.repositories.contacts_repo import ContactRepository
from src.models.contact_model import Contact_model
from src.models.user_model import User
from src.schemas.contact import ContactSchema, ContactUpdateSchema

@pytest.fixture
def mock_session():
    mock_session = AsyncMock(spec=AsyncSession)
    return mock_session

@pytest.fixture
def contact_repository(mock_session):
    return ContactRepository(mock_session)

@pytest.fixture
def user():
    return User(id=1, username="testuser")

@pytest.mark.asyncio
async def test_get_contacts(contact_repository, mock_session, user):
    
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [
        Contact_model(id=1, first_name="John", last_name="Doe", email="john.doe@example.com", user_id=user.id)
    ]
    mock_session.execute = AsyncMock(return_value=mock_result)

    
    contacts = await contact_repository.get_contacts(user=user)

    
    assert len(contacts) == 1
    assert contacts[0].first_name == "John"
    assert contacts[0].last_name == "Doe"
    assert contacts[0].email == "john.doe@example.com"

@pytest.mark.asyncio
async def test_get_contact_by_id(contact_repository, mock_session, user):
    
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = Contact_model(id=1, first_name="John", last_name="Doe", email="john.doe@example.com", user_id=user.id)
    mock_session.execute = AsyncMock(return_value=mock_result)

   
    contact = await contact_repository.get_contact_by_id(contact_id=1, user=user)

    
    assert contact is not None
    assert contact.id == 1
    assert contact.first_name == "John"
    assert contact.last_name == "Doe"
    assert contact.email == "john.doe@example.com"

@pytest.mark.asyncio
async def test_create_contact(contact_repository, mock_session, user):
    
    contact_data = ContactSchema(first_name="John", last_name="Doe", email="john.doe@example.com")

   
    result = await contact_repository.create_contact(body=contact_data, user=user)

  
    assert isinstance(result, Contact_model)
    assert result.first_name == "John"
    assert result.last_name == "Doe"
    assert result.email == "john.doe@example.com"
    mock_session.add.assert_called_once_with(result)
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once_with(result)

@pytest.mark.asyncio
async def test_remove_contact(contact_repository, mock_session, user):
   
    existing_contact = Contact_model(id=1, first_name="John", last_name="Doe", email="john.doe@example.com", user_id=user.id)
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = existing_contact
    mock_session.execute = AsyncMock(return_value=mock_result)

   
    result = await contact_repository.remove_contact(contact_id=1, user=user)

   
    assert result is not None
    assert result.id == 1
    mock_session.delete.assert_awaited_once_with(existing_contact)
    mock_session.commit.assert_awaited_once()

@pytest.mark.asyncio
async def test_update_contact(contact_repository, mock_session, user):
    
    existing_contact = Contact_model(id=1, first_name="John", last_name="Doe", email="john.doe@example.com", user_id=user.id)
    update_data = ContactUpdateSchema(first_name="Jane")
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = existing_contact
    mock_session.execute = AsyncMock(return_value=mock_result)

    
    result = await contact_repository.update_contact(contact_id=1, body=update_data, user=user)

   
    assert result is not None
    assert result.first_name == "Jane"
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once_with(existing_contact)

