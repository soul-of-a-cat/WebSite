import datetime
from typing import List, Optional

from sqlalchemy import Integer, DateTime, ForeignKey, Text, String

from core.models.base import AbstractNameModel, AbstractImageModel
from sqlalchemy.orm import Mapped, mapped_column, relationship

class PostModel(AbstractNameModel):
    __abstract__ = False
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )
    text: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )
    created: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
        default=datetime.datetime.now(datetime.timezone.utc)
    )
    updated: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
        default=datetime.datetime.now(datetime.timezone.utc),
        onupdate=datetime.datetime.now(datetime.timezone.utc)
    )
    images: Mapped[List["PostImageModel"]] = relationship(
        "PostImageModel",
        back_populates="post",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    def get_main_image(self):
        if self.images:
            return self.images[0]
        return None

    def get_all_images_urls(self, request=None) -> List[Optional[str]]:
        return [img.get_image_url(request) for img in self.images if img.has_image()]

    def __repr__(self):
        return f"<Post(id={self.id}, name={self.name[:30]})>"

class PostImageModel(AbstractImageModel):
    __abstract__ = False
    __tablename__ = "post_images"

    IMAGE_SUBFOLDER = "posts"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )
    post_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(
            "posts.id",
            ondelete='CASCADE',
            onupdate='CASCADE',
        ),
        nullable=False,
        index=True
    )
    post: Mapped["PostModel"] = relationship(
        "PostModel",
        back_populates='images'
    )

    order: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Порядок отображения"
    )

    alt_text: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="Alt текст для изображения"
    )

    title: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="Заголовок изображения"
    )

    def __repr__(self):
        return f"<PostImage(id={self.id}, post_id={self.post_id}, order={self.order})>"
