import os
import re
import uuid
from typing import Tuple, Optional

import aiofiles
from PIL import Image
from io import BytesIO
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    declared_attr
)
from sqlalchemy import (
    String,
    Boolean, event
)
import transliterate
from database import Base
from pathlib import Path

from core.config import settings

ONLY_LETTERS_REGEX = re.compile(r"\W")

UPLOAD_DIR = Path(settings.UPLOAD_DIR)

def get_path_image(instance, filename):
    ext = filename.split(".")[-1]
    return f"posts/{uuid.uuid4()}.{ext}"

class AbstractNameModel(Base):
    __abstract__ = True

    is_published: Mapped[bool] = mapped_column(
        Boolean,
        default=True
    )

    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )

    normalized_name: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
        index=True
    )

    def _generate_normalized_name(self) -> str:
        try:
            transliterated = transliterate.translit(
                self.name.lower(),
                reversed=True
            )
        except transliterate.exceptions.LanguageDetectionError:
            transliterated = self.name.lower()

        return ONLY_LETTERS_REGEX.sub("", transliterated)

    def set_normalized_name(self) -> None:
        if self.name:
            self.normalized_name = self._generate_normalized_name()

class AbstractImageModel(Base):
    __abstract__ = True

    IMAGE_SUBFOLDER: str = "images"
    THUMBNAIL_SIZE: Tuple[int, int] = settings.THUMBNAIL_SIZES["medium"]
    CREATE_THUMBNAIL: bool = True
    ALLOWED_EXTENSIONS: Tuple[str, ...] = tuple(settings.ALLOWED_IMAGE_EXTENSIONS)
    MAX_FILE_SIZE: int = settings.MAX_UPLOAD_SIZE

    image_filename: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    image_original_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    image_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

    def _get_upload_folder(self) -> Path:
        folder = UPLOAD_DIR / self.IMAGE_SUBFOLDER
        folder.mkdir(parents=True, exist_ok=True)
        return folder

    @staticmethod
    def _generate_filename(original_filename:str) -> str:
        ext = original_filename.split(".")[-1] if '.' in original_filename else "jpg"
        return f"{uuid.uuid4()}.{ext}"

    @classmethod
    def validate_image(cls, filename: str, file_size: int) -> Tuple[bool, str]:
        ext = os.path.splitext(filename)[1].lower()
        if ext not in cls.ALLOWED_EXTENSIONS:
            return False, f"Unsupported file type: {ext}. Allowed extensions: {cls.ALLOWED_EXTENSIONS}"

        if file_size > cls.MAX_FILE_SIZE:
            return False, f"File too large. Max size {cls.MAX_FILE_SIZE / (1024 ** 2)} MB"

        return True, ""

    async def save_image(self, file_data: bytes, original_filename: str) -> dict:
        is_valid, error_msg = self.validate_image(original_filename, len(file_data))
        if not is_valid:
            raise ValueError(error_msg)

        await self.delete_image()

        filename = self._generate_filename(original_filename)
        folder = self._get_upload_folder()
        file_path = folder / filename

        async with aiofiles.open(file_path, "wb") as file:
            await file.write(file_data)

        if self.CREATE_THUMBNAIL:
            await self._create_thumbnail(file_data, filename)

        self.image_filename = filename
        self.image_original_name = original_filename
        self.image_path = f"{self.IMAGE_SUBFOLDER}/{filename}"

        return {
            "filename": self.image_filename,
            "original_name": self.image_original_name,
            "path": self.image_path,
            "full_path": str(file_path)
        }

    async def _create_thumbnail(self, file_data: bytes, filename: str) -> None:
        try:
            img = Image.open(BytesIO(file_data))

            if img.mode in ("RGBA", "LA", "P"):
                background = Image.new("RGB", img.size, (255, 255, 255))
                if img.mode == "P":
                    img = img.convert("RGBA")
                background.paste(img, mask=img.split()[-1] if img.mode == "RGBA" else None)
                img = background

            img.thumbnail(self.THUMBNAIL_SIZE, Image.Resampling.LANCZOS)

            thumb_folder = self._get_upload_folder() / "thumbnails"
            thumb_folder.mkdir(parents=True, exist_ok=True)

            thumbnail_path = thumb_folder / f"thumb_{filename}"

            save_format = img.format or "JPEG"
            if save_format.upper() == "JPEG":
                img.save(thumbnail_path, format="JPEG", quality=85, optimize=True)
            else:
                img.save(thumbnail_path, format=save_format, optimize=True)
        except Exception as e:
            print(f"Thumbnail creation failed: {e}")

    async def delete_image(self) -> bool:
        if not self.image_filename:
            return False

        try:
            file_path = self._get_upload_folder() / self.image_filename
            if file_path.exists():
                os.remove(file_path)

            thumb_path = self._get_upload_folder() / "thumbnails" / f"thumb_{self.image_filename}"
            if thumb_path.exists():
                os.remove(thumb_path)

            self.image_original_name = None
            self.image_path = None
            self.image_filename = None

            return True
        except Exception as e:
            print(f"Image deletion failed: {e}")
            return False

    def get_image_url(self, request=None) -> Optional[str]:
        if not self.image_filename:
            return None

        base_url = f"{request.base_url}" if request else "/"
        return f"{base_url}{settings.MEDIA_URL}{self.image_path}"

    def get_thumbnail_url(self, request=None) -> Optional[str]:
        if not self.image_filename:
            return None

        base_url = f"{request.base_url}" if request else "/"
        thumb_path = f"{self.IMAGE_SUBFOLDER}/thumbnails/thumb_{self.image_filename}"
        return f"{base_url}{settings.MEDIA_URL}{thumb_path}"

    def has_image(self) -> bool:
        return bool(self.image_filename)

@event.listens_for(AbstractNameModel, 'before_insert')
@event.listens_for(AbstractNameModel, 'before_update')
def set_normalized_name(mapper, connection, target):
    if target.name and not target.normalized_name:
        target.set_normalized_name()