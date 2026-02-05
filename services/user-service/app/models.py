from datetime import datetime, date
from typing import Optional
import re

from sqlalchemy import String, DateTime, Boolean, Integer, ForeignKey, Date, event
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates, selectinload

from database import AsyncSession

from database import Base
import hashlib
from PIL import Image as PILImage
import io
import aiofiles
from pathlib import Path


class UserManager:
    CANONICAL_DOMAINS = {
        "ya.ru": "yandex.ru",
        "yandex.com": "yandex.ru",
        "narod.ru": "yandex.ru",
    }

    DOTS = {
        "yandex.ru": "-",
        "gmail.com": "",
        "googlemail.com": "",
    }

    @classmethod
    def normalize_email(cls, email: str) -> str:
        # Нормализация email
        if not email:
            return email

        email = email.strip().lower()

        try:
            email_name, domain_part = email.rsplit("@", 1)

            if "+" in email_name:
                email_name = email_name.split("+", 1)[0]

            domain_part = cls.CANONICAL_DOMAINS.get(domain_part, domain_part)

            replace_char = cls.DOTS.get(domain_part, ".")
            email_name = email_name.replace(".", replace_char)

            email_name = re.sub(r'[^\w.+-]', '', email_name)

        except ValueError:
            return email

        return f"{email_name}@{domain_part}"

    @classmethod
    def normalize_username(cls, username: str) -> str:
        # Нормализация имени пользователя
        return username.strip().lower()


class User(Base):
    __tablename__ = "User"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    password: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
        comment="Пароль"
    )
    last_login: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
        comment="Последний вход"
    )
    is_superuser: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Суперпользователь"
    )
    username: Mapped[str] = mapped_column(
        String(150),
        unique=True,
        nullable=False,
        index=True,
        comment="Никнейм пользователя"
    )
    first_name: Mapped[str] = mapped_column(
        String(150),
        default="",
        nullable=False,
        comment="Имя пользователя"
    )
    last_name: Mapped[str] = mapped_column(
        String(150),
        default="",
        nullable=False,
        comment="Фамилия пользователя"
    )
    email: Mapped[str] = mapped_column(
        String(150),
        unique=True,
        nullable=False,
        index=True,
        comment="Почта"
    )
    is_staff: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Персонал"
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Активный"
    )
    date_joined: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        nullable=False,
        comment="Дата регистрации"
    )

    profile: Mapped["Profile"] = relationship(
        "Profile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    @validates('email')
    def validate_email(self, key: str, email: str) -> str:
        # Валидация и нормализация email при сохранении
        return UserManager.normalize_email(email)

    @classmethod
    async def get_active_users(cls, session: AsyncSession):
        # Получить активных пользователей
        from sqlalchemy import select
        stmt = select(cls).where(
            cls.is_active == True
        ).options(selectinload(cls.profile))
        result = await session.execute(stmt)
        return result.scalars().all()

    @classmethod
    async def by_email(cls, session: AsyncSession, email: str):
        from sqlalchemy import select
        normalized_email = UserManager.normalize_email(email)
        stmt = select(cls).where(
            cls.email == normalized_email,
            cls.is_active == True
        ).options(selectinload(cls.profile))
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @classmethod
    async def by_username(cls, session: AsyncSession, username: str):
        from sqlalchemy import select
        normalized_username = UserManager.normalize_username(username)
        stmt = select(cls).where(
            cls.username == normalized_username,
            cls.is_active == True
        ).options(selectinload(cls.profile))
        result = await session.execute(stmt)
        return result.scalar_one_or_none()


class Profile(Base):
    __tablename__ = "Profile"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("User.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
        comment="ID пользователя"
    )
    birthday: Mapped[Optional[date]] = mapped_column(
        Date,
        nullable=True,
        comment="Дата рождения"
    )
    attempts_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Количество попыток входа"
    )
    block_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
        comment="Дата блокировки"
    )
    image: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment="Путь к аватарке"
    )

    user: Mapped["User"] = relationship(
        "User",
        back_populates="profile",
        lazy="joined"
    )

    IMAGE_BASE_DIR = Path("static/users")
    THUMBNAIL_DIR = "thumbnails"

    @property
    def image_upload_path(self) -> Path:
        # Путь для загрузки изображений пользователя
        return self.IMAGE_BASE_DIR / str(self.user_id)

    async def save_image(self, file_data: bytes, filename: str) -> str:
        # Сохранение загруженного изображения
        await aiofiles.os.makedirs(self.image_upload_path, exist_ok=True)

        filepath = self.image_upload_path / filename

        async with aiofiles.open(filepath, 'wb') as f:
            await f.write(file_data)

        self.image = str(filepath)

        await self._create_thumbnail(filepath, 300, 300)
        await self._create_thumbnail(filepath, 50, 50)

        return self.image

    async def get_image_url(self, size: str = "original") -> Optional[str]:
        # Получить URL изображения заданного размера
        if not self.image:
            return None

        if size == "300x300":
            return await self._get_thumbnail_url(300, 300)
        elif size == "50x50":
            return await self._get_thumbnail_url(50, 50)

        return self.image

    async def _get_thumbnail_url(self, width: int, height: int) -> Optional[str]:
        # Получить URL миниатюры
        if not self.image:
            return None

        original_path = Path(self.image)

        hash_name = hashlib.md5(
            f"{original_path.stem}_{width}x{height}".encode()
        ).hexdigest()[:8]

        thumbnail_name = f"{original_path.stem}_{width}x{height}_{hash_name}{original_path.suffix}"
        thumbnail_path = original_path.parent / self.THUMBNAIL_DIR / thumbnail_name

        try:
            if await aiofiles.os.path.exists(thumbnail_path):
                return str(thumbnail_path)
        except:
            pass

        if await self._create_thumbnail(original_path, width, height):
            return str(thumbnail_path)

        return None

    async def _create_thumbnail(self, source_path: Path, width: int, height: int) -> bool:
        try:
            try:
                async with aiofiles.open(source_path, 'rb') as f:
                    image_data = await f.read()
            except FileNotFoundError:
                print(f"Source file not found: {source_path}")
                return False

            thumbnail_dir = source_path.parent / self.THUMBNAIL_DIR
            await aiofiles.os.makedirs(thumbnail_dir, exist_ok=True)

            hash_name = hashlib.md5(
                f"{source_path.stem}_{width}x{height}".encode()
            ).hexdigest()[:8]
            thumbnail_name = f"{source_path.stem}_{width}x{height}_{hash_name}{source_path.suffix}"
            thumbnail_path = thumbnail_dir / thumbnail_name

            image = PILImage.open(io.BytesIO(image_data))

            if image.mode in ('RGBA', 'LA'):
                background = PILImage.new('RGB', image.size, (255, 255, 255))
                background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                image = background
            elif image.mode == 'P':
                image = image.convert('RGB')

            image = self._crop_center(image, width, height)

            image.save(thumbnail_path, quality=85, optimize=True)
            return True

        except Exception as e:
            print(f"Error creating thumbnail: {e}")
            return False

    def _crop_center(self, image: PILImage.Image, width: int, height: int) -> PILImage.Image:
        img_width, img_height = image.size

        target_ratio = width / height
        img_ratio = img_width / img_height

        if img_ratio > target_ratio:
            new_width = int(img_height * target_ratio)
            left = (img_width - new_width) // 2
            right = left + new_width
            top = 0
            bottom = img_height
        else:
            new_height = int(img_width / target_ratio)
            top = (img_height - new_height) // 2
            bottom = top + new_height
            left = 0
            right = img_width

        cropped = image.crop((left, top, right, bottom))
        return cropped.resize((width, height), PILImage.Resampling.LANCZOS)

    def increment_attempts(self) -> None:
        # Увеличить счетчик попыток входа
        self.attempts_count += 1

    def reset_attempts(self) -> None:
        # Сбросить счетчик попыток входа
        self.attempts_count = 0

    def block_user(self) -> None:
        # Заблокировать пользователя
        self.block_date = datetime.now()

    def unblock_user(self) -> None:
        # Разблокировать пользователя
        self.block_date = None
        self.reset_attempts()

    def is_blocked(self) -> bool:
        # Проверка, заблокирован ли пользователь
        if not self.block_date:
            return False

        time_since_block = datetime.now() - self.block_date
        if time_since_block.total_seconds() > 24 * 60 * 60:
            self.unblock_user()
            return False

        return True


@event.listens_for(User, 'after_insert')
def create_profile(mapper, connection, target):
    # Автоматическое создание профиля при создании пользователя
    from sqlalchemy import insert
    profile_table = Profile.__table__

    connection.execute(
        insert(profile_table).values(
            user_id=target.id,
            attempts_count=0
        )
    )