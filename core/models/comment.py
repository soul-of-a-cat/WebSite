from typing import Optional, List
from sqlalchemy import Integer, DateTime, ForeignKey, Text, String
from core.models.base import AbstractNameModel, AbstractImageModel
from sqlalchemy.orm import Mapped, mapped_column, relationship
import datetime

class CommentModel(AbstractNameModel):
    __abstract__ = False
    __tablename__ = 'comments'

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
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
    images: Mapped[List["CommentImageModel"]] = relationship(
        "CommentImageModel",
        back_populates="comment",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    def get_all_images_url(self, request=None) -> List[Optional[str]]:
        return [img.get_image_url(request) for img in self.images if img.has_image()]

    def __repr__(self):
        return f"<Comment(id={self.id}, name={self.name[:30]})>"

    class CommentImageModel(AbstractImageModel):
        __abstract__ = False
        __tablename__ = 'comment_images'

        IMAGE_SUBFOLDER = "comments"

        id: Mapped[int] = mapped_column(
            Integer,
            primary_key=True,
            autoincrement=True
        )
        comment_id: Mapped[int] = mapped_column(
            Integer,
            ForeignKey(
                'comments.id',
                ondelete='CASCADE',
                onupdate='CASCADE',
            ),
            nullable=False,
            index=True,
        )

        comment: Mapped["CommentModel"] = relationship(
            "CommentModel",
            back_populates="images",
        )

        order: Mapped[int] = mapped_column(
            Integer,
            default=0,
            nullable=False,
            comment="Порядок отображения"
        )

        alt_text: Mapped[str] = mapped_column(
            String(255),
            nullable=True,
            comment="Alt текст для изображения"
        )

        title: Mapped[str] = mapped_column(
            String(255),
            nullable=True,
            comment="Заголовок изображения"
        )

        def __repr__(self):
            return f"<CommentImage(id={self.id}, comment_id={self.comment_id}, order={self.order})>"