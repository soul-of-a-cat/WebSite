import os
import re
import uuid
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Optional, ClassVar
from urllib.parse import urljoin

import aiofiles
from aiofiles.os import makedirs
from fastapi import HTTPException, UploadFile
from sqlalchemy import Boolean, String, Integer, DateTime, ForeignKey, select
from sqlalchemy.orm import Mapped, mapped_column, validates, relationship, DeclarativeBase
from sqlalchemy import exists
from transliterate import translit
from database import AsyncSession, Base
from PIL import Image
from datetime import datetime

ONLY_LETTERS_REGEX = re.compile(r"\W")

ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif'}

async def get_path_image(filename: str) -> str:
    if '.' in filename:
        name, ext = filename.rsplit('.', 1)
        return f"posts/{uuid.uuid4()}.{ext.lower()}"
    return f"posts/{uuid.uuid4()}.jpg"


class Post(Base):
    __tablename__ = "Post"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    is_published: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Опубликовано"
    )
    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
        index=True,
        comment="Название, max 150 символов"
    )
    normalized_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
        index=True,
        comment="Нормализованное название"
    )

    user_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    text: Mapped[str] = mapped_column(String, nullable=False, index=True)

    created: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        index=True,
        default=datetime.utcnow
    )
    updated: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        index=True,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    images: Mapped[list["PostImage"]] = relationship(
        "PostImage",
        back_populates="post",
        cascade="all, delete-orphan",
        lazy="select",
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if 'normalized_name' not in kwargs and 'name' in kwargs:
            self.normalized_name = self._generate_normalized_name(kwargs['name'])

    @classmethod
    async def validate_unique_normalized_name(
            cls,
            db: AsyncSession,
            normalized_name: str,
            obj_id: Optional[int] = None
    ):
        stmt = select(cls).where(cls.normalized_name == normalized_name)
        if obj_id:
            stmt = stmt.where(cls.id != obj_id)

        result = await db.execute(select(exists().where(stmt)))
        if result.scalar():
            raise HTTPException(
                status_code=400,
                detail="Уже есть такой же элемент"
            )

    def _generate_normalized_name(self, name: str) -> str:
        try:
            transliterated = translit(
                name.lower(),
                'ru',
                reversed=True
            )
        except Exception:
            transliterated = name.lower()

        normalized = ONLY_LETTERS_REGEX.sub("", transliterated)
        return normalized

    @validates('name')
    def validate_name(self, key, name):
        if len(name) > 150:
            raise ValueError("Максимальная длина названия - 150 символов")

        self.normalized_name = self._generate_normalized_name(name)
        return name


class PostImage(Base):
    __tablename__ = "PostImage"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    image_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    thumbnail_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    post_id: Mapped[int] = mapped_column(Integer, ForeignKey("Post.id", ondelete="CASCADE"), nullable=False, index=True)

    post: Mapped["Post"] = relationship("Post", back_populates="images")

    STATIC_DIR: ClassVar[str] = "static"
    IMAGE_UPLOAD_DIR: ClassVar[str] = "posts/"
    THUMBNAIL_SIZE: ClassVar[tuple[int, int]] = (300, 300)

    @property
    def image_url(self) -> Optional[str]:
        if self.image_path:
            return urljoin("/media/", self.image_path)
        return None

    @property
    def thumbnail_url(self) -> Optional[str]:
        if self.thumbnail_path:
            return urljoin("/media/", self.thumbnail_path)
        return None

    async def save_image(self, image_file: UploadFile, db: AsyncSession):
        try:
            file_extension = os.path.splitext(image_file.filename)[1].lower()
            if file_extension not in ALLOWED_EXTENSIONS:
                raise HTTPException(status_code=400, detail="Неподдерживаемый формат файла")

            MAX_SIZE = 10 * 1024 * 1024  # 10MB

            original_filename = image_file.filename

            content = await image_file.read()
            if len(content) > MAX_SIZE:
                raise HTTPException(status_code=400, detail="Файл слишком большой")

            filename = await get_path_image(original_filename)

            image_path = os.path.join(self.STATIC_DIR, self.IMAGE_UPLOAD_DIR, filename)
            await makedirs(os.path.dirname(image_path), exist_ok=True)

            async with aiofiles.open(image_path, 'wb') as out_file:
                await out_file.write(content)

            thumbnail_path = os.path.join(self.STATIC_DIR, self.IMAGE_UPLOAD_DIR, f"thumb_{filename}")
            await self._create_thumbnail(image_path, thumbnail_path)

            self.image_path = os.path.join(self.IMAGE_UPLOAD_DIR, filename)
            self.thumbnail_path = os.path.join(self.IMAGE_UPLOAD_DIR, f"thumb_{filename}")
            await db.flush()

            return self
        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=500, detail=f"Ошибка сохранения изображения: {str(e)}")

    async def _create_thumbnail(self, original_path: str, thumbnail_path: str):
        def create_thumbnail_sync():
            with Image.open(original_path) as image:
                image.thumbnail(self.THUMBNAIL_SIZE, Image.Resampling.LANCZOS)
                ext = os.path.splitext(original_path)[1].lower()
                if ext in ['.jpg', '.jpeg']:
                    image.save(thumbnail_path, "JPEG", quality=85)
                elif ext == '.png':
                    image.save(thumbnail_path, "PNG")
                else:
                    image.save(thumbnail_path)

        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as pool:
            await loop.run_in_executor(pool, create_thumbnail_sync())