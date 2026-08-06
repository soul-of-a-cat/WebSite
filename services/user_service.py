from fastapi import UploadFile, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from schemas.user import UserCreate, UserUpdate
from models.user import User, Profile


class UserService:
    @staticmethod
    async def create(
            session: AsyncSession,
            data: UserCreate,
    ):
        user = User(
            username=data.username,
            email=data.email,
        )
        user.set_password(data.password)

        profile = Profile(
            user=user
        )

        session.add(user)
        session.add(profile)
        await session.commit()

        return user

    @staticmethod
    async def delete(
            session: AsyncSession,
            user: User
    ):
        await session.delete(user)
        await session.commit()

    @staticmethod
    async def authenticate(
            session: AsyncSession,
            email: str,
            password: str
    ):
        user = await UserService.get_by_email(session, email)

        if user is None:
            raise HTTPException(404, "Пользователь не найден")

        if not user.verify_password(password):
            raise HTTPException(404, "Неверный пароль")

        return user

    @staticmethod
    async def get_by_email(
            session: AsyncSession,
            email: str
    ) -> User | None:
        result = await session.execute(
            select(User)
            .where(User.email == email)
        )

        user = result.scalar_one_or_none()

        return user

    @staticmethod
    async def get_by_id(
            session: AsyncSession,
            user_id: int
    ):
        result = await session.execute(
            select(User)
            .where(User.id == user_id)
        )

        user = result.scalar_one_or_none()

        return user

    @staticmethod
    async def get_by_username(
            session: AsyncSession,
            username: str
    ):
        result = await session.execute(
            select(User)
            .where(User.username == username)
        )

        user = result.scalar_one_or_none()

        return user

    @staticmethod
    async def update(
            session: AsyncSession,
            user_id: int,
            data: UserUpdate
    ):
        result = await session.execute(
            select(User)
            .where(User.id == user_id)
        )

        user = result.scalar_one_or_none()

        if user is None:
            raise HTTPException(404, "Пользователь не найден")

        user.username = data.username
        user.email = data.email
        user.first_name = data.first_name
        user.last_name = data.last_name

        await session.commit()
        await session.refresh(user)

        return user

    @staticmethod
    async def change_password(
            session: AsyncSession,
            old_password: str,
            new_password: str,
            user_id: int
    ):
        result = await session.execute(
            select(User)
            .where(User.id == user_id)
        )

        user = result.scalar_one_or_none()

        if user is None:
            raise HTTPException(404, "Пользователь не найден")

        user.set_password(new_password)

        await session.commit()
        await session.refresh(user)

        return user
