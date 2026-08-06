from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_async_session
from models.user import User

async def get_current_user(
        session: AsyncSession = Depends(get_async_session)
) -> User:
    return await session.get(User, 1)