import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.user_model import User
from src.repositories.base_repo import BaseRepository
from src.schemas.user import UserCreate

logger = logging.getLogger("uvicorn.error")


class UserRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        """
        Initialize the UserRepository.

        Args:
            session: An AsyncSession object connected to the database.
        """
        super().__init__(session, User)

    async def get_by_username(self, username: str) -> User | None:
        """
        Retrieve a user by their username.

        Args:
            username: The username of the user to retrieve.

        Returns:
            The User with the specified username, or None if no such user exists.
        """
        stmt = select(self.model).where(self.model.username == username)
        user = await self.db.execute(stmt)
        return user.scalar_one_or_none()

    async def get_user_by_email(self, email: str) -> User | None:
        """
        Retrieve a user by their email.

        Args:
            email: The email of the user to retrieve.

        Returns:
            The User with the specified email, or None if no such user exists.
        """
        stmt = select(self.model).where(self.model.email == email)
        user = await self.db.execute(stmt)
        return user.scalar_one_or_none()

    async def create_user(
        self, user_data: UserCreate, hashed_password: str, avatar: str
    ) -> User:
        """
        Create a new user with the specified data.

        Args:
            user_data: A UserCreate object containing the user data.
            hashed_password: The hashed password for the user.
            avatar: The URL of the user's avatar.

        Returns:
            The newly created User object.
        """
        user = User(
            **user_data.model_dump(exclude_unset=True, exclude={"password"}),
            hash_password=hashed_password,
            avatar=avatar
        )
        return await self.create(user)

    async def confirmed_email(self, email: str) -> None:
        """
        Mark a user's email as confirmed.

        Args:
            email: The email of the user whose email confirmation status needs to be updated.
        
        Returns:
            None
        """
        user = await self.get_user_by_email(email)
        user.confirmed = True
        await self.db.commit()

    async def update_avatar_url(self, email: str, url: str) -> User:
        """
        Update a user's avatar URL.

        Args:
            email: The email of the user whose avatar URL needs to be updated.
            url: The new avatar URL.

        Returns:
            The updated User object with the new avatar URL.
        """
        user = await self.get_user_by_email(email)
        user.avatar = url
        await self.db.commit()
        await self.db.refresh(user)
        return user
    
    async def update_password(self, user: User, new_hashed_password: str):
        user.hash_password = new_hashed_password
        await self.db.commit()
        return user