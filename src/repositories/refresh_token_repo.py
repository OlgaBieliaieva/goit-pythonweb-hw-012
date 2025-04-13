import logging
from datetime import datetime
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.user_model import RefreshToken
from src.repositories.base_repo import BaseRepository

logger = logging.getLogger("uvicorn.error")


class RefreshTokenRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        """
        Initialize the RefreshTokenRepository.

        Args:
            session: An AsyncSession object connected to the database.
        """
        super().__init__(session, RefreshToken)

    async def get_by_token_hash(self, token_hash: str) -> RefreshToken | None:
        """
        Retrieve a refresh token by its hash.

        Args:
            token_hash: The hash of the refresh token to retrieve.

        Returns:
            The RefreshToken with the specified hash, or None if no such token exists.
        """
        stmt = select(self.model).where(RefreshToken.token_hash == token_hash)
        token = await self.db.execute(stmt)
        return token.scalars().first()

    async def get_active_token(
        self, token_hash: str, current_time: datetime
    ) -> RefreshToken | None:
        """
        Retrieve an active refresh token by its hash.

        Args:
            token_hash: The hash of the refresh token to retrieve.
            current_time: The current time used to check if the token is still valid.

        Returns:
            The active RefreshToken with the specified hash, or None if no such active token exists.
        """
        stmt = select(self.model).where(
            RefreshToken.token_hash == token_hash,
            RefreshToken.expired_at > current_time,
            RefreshToken.revoked_at.is_(None),
        )
        token = await self.db.execute(stmt)
        return token.scalars().first()

    async def save_token(
        self,
        user_id: int,
        token_hash: str,
        expired_at: datetime,
        ip_address: str,
        user_agent: str,
    ) -> RefreshToken:
        """
        Save a new refresh token to the database.

        Args:
            user_id: The ID of the user for whom the refresh token is created.
            token_hash: The hash of the refresh token.
            expired_at: The expiration date and time of the refresh token.
            ip_address: The IP address from which the refresh token was created.
            user_agent: The user agent (browser) that created the refresh token.

        Returns:
            The newly created RefreshToken object.
        """
        refresh_token = RefreshToken(
            user_id=user_id,
            token_hash=token_hash,
            expired_at=expired_at,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        return await self.create(refresh_token)

    async def revoke_token(self, refresh_token: RefreshToken) -> None:
        """
        Revoke a refresh token by setting its revoked_at timestamp.

        Args:
            refresh_token: The refresh token to be revoked.

        Returns:
            None
        """
        refresh_token.revoked_at = datetime.now()
        await self.db.commit()