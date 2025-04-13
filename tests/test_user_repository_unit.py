import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.users_repo import UserRepository
from src.models.user_model import User
from src.schemas.user import UserCreate


@pytest.fixture
def mock_session():
    mock_session = AsyncMock(spec=AsyncSession)
    return mock_session


@pytest.fixture
def user_repository(mock_session):
    return UserRepository(mock_session)


@pytest.fixture
def user_data():
    return UserCreate(username="testuser", email="test@example.com")

@pytest.mark.asyncio
async def test_get_by_username(user_repository, mock_session):
    
    mock_user = User(id=1, username="testuser", email="test@example.com", hash_password="hashed_pw", avatar="avatar_url")
    mock_session.execute = AsyncMock(return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=mock_user)))

   
    user = await user_repository.get_by_username("testuser")

    
    assert user is not None
    assert user.username == "testuser"

@pytest.mark.asyncio
async def test_get_user_by_email(user_repository, mock_session):
    
    mock_user = User(id=1, username="testuser", email="test@example.com", hash_password="hashed_pw", avatar="avatar_url")
    mock_session.execute = AsyncMock(return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=mock_user)))

    
    user = await user_repository.get_user_by_email("test@example.com")

   
    assert user is not None
    assert user.email == "test@example.com"

@pytest.mark.asyncio
async def test_create_user(user_repository, mock_session, user_data):
    
    hashed_password = "hashed_pw"
    avatar = "avatar_url"
    new_user = User(
        id=1,
        username=user_data.username,
        email=user_data.email,
        hash_password=hashed_password,
        avatar=avatar
    )
    
    
    mock_session.execute = AsyncMock(return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=new_user)))

   
    result = await user_repository.create_user(user_data, hashed_password, avatar)

   
    assert result.username == "testuser"
    assert result.email == "test@example.com"
    mock_session.add.assert_called_once()
    mock_session.commit.assert_awaited_once()

@pytest.mark.asyncio
async def test_confirmed_email(user_repository, mock_session):
    
    mock_user = User(id=1, username="testuser", email="test@example.com", hash_password="hashed_pw", avatar="avatar_url", confirmed=False)
    mock_session.execute = AsyncMock(return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=mock_user)))

   
    await user_repository.confirmed_email("test@example.com")

    
    assert mock_user.confirmed is True
    mock_session.commit.assert_awaited_once()

@pytest.mark.asyncio
async def test_update_avatar_url(user_repository, mock_session):
    
    mock_user = User(id=1, username="testuser", email="test@example.com", hash_password="hashed_pw", avatar="old_avatar_url")
    mock_session.execute = AsyncMock(return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=mock_user)))
    
    new_avatar_url = "new_avatar_url"

    
    result = await user_repository.update_avatar_url("test@example.com", new_avatar_url)

    
    assert result.avatar == new_avatar_url
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once_with(mock_user)