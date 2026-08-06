from fastapi import UploadFile, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from schemas.user import UserCreate, UserUpdate, ProfileUpdate
from models.user import User, Profile


class ProfileService:
    @staticmethod
    async def get_by_user(
            session: AsyncSession,
            user_id: int,
    ):
        result = await session.execute(
            select(Profile)
            .where(Profile.user_id == user_id)
        )

        profile = result.scalar_one_or_none()

        if profile is None:
            return None

        return profile

    @staticmethod
    async def update(
            session: AsyncSession,
            user_id: int,
            data: ProfileUpdate
    ):

        result = await session.execute(
            select(Profile)
            .where(Profile.user_id == user_id)
        )

        profile = result.scalar_one_or_none()

        if profile is None:
            return HTTPException(status_code=404, detail="Профиль не найден")

        profile.birthday = data.birthday

        await session.commit()
        await session.refresh(profile)

        return profile

    @staticmethod
    async def upload_avatar(
            session: AsyncSession,
            user_id: int,
            image: UploadFile,
    ):
        result = await session.execute(
            select(Profile)
            .where(Profile.user_id == user_id)
        )

        profile = result.scalar_one_or_none()

        if profile is None:
            return HTTPException(status_code=404, detail="Профиль не найден")

        await profile.save_upload(image)

        await session.commit()

        return profile

    @staticmethod
    async def delete_avatar(
            session: AsyncSession,
            user_id: int
    ):
        result = await session.execute(
            select(Profile)
            .where(Profile.user_id == user_id)
        )

        profile = result.scalar_one_or_none()

        if profile is None:
            return HTTPException(status_code=404, detail="Профиль не найден")

        await profile.delete_image()

        await session.commit()
        await session.refresh(profile)

        return profile